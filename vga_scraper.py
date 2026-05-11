import os
import re
import json
import asyncio
import pandas as pd
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from playwright.async_api import async_playwright
import httpx
import openpyxl
from openpyxl.worksheet.table import Table, TableStyleInfo

load_dotenv()

class VGAScraper:
    def __init__(self):
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        self.gearvn_urls = [
            "https://gearvn.com/collections/vga-rtx-50-series",
            "https://gearvn.com/collections/vga-card-man-hinh"
        ]
        self.thns_url = "https://tinhocngoisao.com/collections/card-man-hinh"
        self.data = []
        self.data = []
    async def send_telegram_alert(self, message: str):
        if not self.telegram_bot_token or not self.telegram_chat_id:
            print(f"[Telegram Not Configured] {message}")
            return
            
        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        payload = {
            "chat_id": self.telegram_chat_id,
            "text": message
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload)
                if response.status_code != 200:
                    print(f"Failed to send telegram alert: {response.text}")
        except Exception as e:
            print(f"Error sending telegram alert: {e}")

    def clean_price(self, price_str):
        if not price_str:
            return 0
        cleaned = re.sub(r'[^\d]', '', price_str)
        return int(cleaned) if cleaned else 0

    async def crawl_gearvn(self, page, url):
        print(f"Crawling GearVN: {url}")
        try:
            await page.goto(url, timeout=60000, wait_until="load")
            await page.wait_for_timeout(3000)
            
            # Dùng CSS ẩn luôn tất cả popup quảng cáo để không bao giờ bị che
            try:
                await page.add_style_tag(content=".modal, .modal-backdrop, #myModal { display: none !important; pointer-events: none !important; z-index: -1 !important; }")
                print("Đã chèn CSS ẩn popup quảng cáo GearVN.")
            except Exception:
                pass
            
            # Xử lý pagination
            selector_load_more = "#load_more"
            
            while True:
                try:
                    button = page.locator(selector_load_more)
                    if await button.count() > 0 and await button.is_visible():
                        current_count = await page.locator('.proloop-block').count()
                        await button.scroll_into_view_if_needed()
                        await page.evaluate("document.querySelectorAll('.modal, .modal-backdrop').forEach(el => el.remove())")
                        await button.click()
                        await page.wait_for_timeout(5000)
                        
                        new_count = await page.locator('.proloop-block').count()
                        if new_count == current_count:
                            break
                    else:
                        break
                except Exception as e:
                    break
                
            blocks = page.locator('.proloop-block')
            count = await blocks.count()
            
            if count == 0:
                await self.send_telegram_alert(f"Lỗi: GearVN không tìm thấy Selector .proloop-block hoặc lỗi kết nối tại {url}")
                return

            for i in range(count):
                block = blocks.nth(i)
                name_loc = block.locator('.proloop-name a')
                name = await name_loc.inner_text() if await name_loc.count() > 0 else ""
                
                product_url_path = await name_loc.get_attribute('href') if await name_loc.count() > 0 else ""
                product_url = f"https://gearvn.com{product_url_path}" if product_url_path else url
                
                highlight_loc = block.locator('.proloop-price--highlight')
                discount_price_str = await highlight_loc.inner_text() if await highlight_loc.count() > 0 else ""
                discount_price = self.clean_price(discount_price_str)
                
                compare_loc = block.locator('.proloop-price--compare del')
                if await compare_loc.count() > 0:
                    original_price_str = await compare_loc.inner_text()
                    original_price = self.clean_price(original_price_str)
                else:
                    original_price = discount_price
                    
                if name:
                    self.data.append({
                        "source": "GearVN",
                        "raw_name": name.strip(),
                        "original_price": original_price,
                        "discount_price": discount_price,
                        "url": product_url
                    })
        except Exception as e:
            await self.send_telegram_alert(f"Lỗi: GearVN lỗi kết nối hoặc xử lý tại {url}. Detail: {str(e)}")

    async def crawl_thns(self, page, url):
        print(f"Crawling Tin Học Ngôi Sao: {url}")
        try:
            await page.goto(url, timeout=60000, wait_until="load")
            await page.wait_for_timeout(3000)
            
            # Dùng CSS ẩn popup/chat widget
            try:
                await page.add_style_tag(content=".modal, .modal-backdrop, [id*='onesignal'], [id*='fb-root'] { display: none !important; pointer-events: none !important; z-index: -1 !important; }")
            except Exception:
                pass
            
            # Xử lý pagination
            selector_load_more = ".btn-load__more"
            
            while True:
                try:
                    button = page.locator(selector_load_more)
                    if await button.count() > 0 and await button.is_visible():
                        current_count = await page.locator('.itemLoop').count()
                        await button.scroll_into_view_if_needed()
                        await page.evaluate("document.querySelectorAll('.modal, .modal-backdrop, [id*=\"onesignal\"]').forEach(el => el.remove())")
                        await button.click()
                        await page.wait_for_timeout(5000)
                        
                        new_count = await page.locator('.itemLoop').count()
                        if new_count == current_count:
                            break
                    else:
                        break
                except Exception as e:
                    break
                    
            blocks = page.locator('.itemLoop')
            count = await blocks.count()
            
            if count == 0:
                await self.send_telegram_alert(f"Lỗi: Tin Học Ngôi Sao không tìm thấy Selector .itemLoop hoặc lỗi kết nối tại {url}")
                return

            for i in range(count):
                block = blocks.nth(i)
                name_loc = block.locator('.pdLoopName a')
                name = await name_loc.inner_text() if await name_loc.count() > 0 else ""
                
                product_url_path = await name_loc.get_attribute('href') if await name_loc.count() > 0 else ""
                product_url = f"https://tinhocngoisao.com{product_url_path}" if product_url_path else url
                
                price_loc = block.locator('.pdPrice span')
                price_count = await price_loc.count()
                
                original_price = 0
                discount_price = 0
                
                if price_count > 0:
                    prices_str = []
                    for j in range(price_count):
                        prices_str.append(await price_loc.nth(j).inner_text())
                    
                    prices = [self.clean_price(p) for p in prices_str if self.clean_price(p) > 0]
                    if len(prices) >= 2:
                        original_price = max(prices)
                        discount_price = min(prices)
                    elif len(prices) == 1:
                        original_price = discount_price = prices[0]

                if name:
                    self.data.append({
                        "source": "Tin Học Ngôi Sao",
                        "raw_name": name.strip(),
                        "original_price": original_price,
                        "discount_price": discount_price,
                        "url": product_url
                    })
        except Exception as e:
            await self.send_telegram_alert(f"Lỗi: Tin Học Ngôi Sao lỗi kết nối hoặc xử lý tại {url}. Detail: {str(e)}")
    async def async_run(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            for url in self.gearvn_urls:
                await self.crawl_gearvn(page, url)
                
            await self.crawl_thns(page, self.thns_url)
            
            await browser.close()
            
        if not self.data:
            await self.send_telegram_alert("Cảnh báo: Không crawl được dữ liệu nào từ các trang.")
            return

        vn_tz = timezone(timedelta(hours=7))
        crawled_date_str = datetime.now(vn_tz).strftime("%d/%m/%Y %H:%M:%S")
        
        excel_path = "vga_data.xlsx"
        
        try:
            if os.path.exists(excel_path):
                wb = openpyxl.load_workbook(excel_path)
            else:
                wb = openpyxl.Workbook()
                sheet = wb.active
                sheet.title = "GPU Lookup"
                sheet.append(["source", "raw_name", "original_price", "discount_price", "url", "crawled_date", "brand", "chipset", "vram_gb"])
                
                ref_sheet = wb.create_sheet(title="GPU ref")
                ref_sheet.append(["GPU brand text", "GPU brand", "", "Chipset text", "Chipset", "", "Video memory text", "Video memory"])
                ref_sheet.append(["ASUS", "ASUS", "", "RTX 3060", "NVIDIA GeForce RTX 3060", "", "8GB", "8GB"])
                
                style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False, showLastColumn=False, showRowStripes=True, showColumnStripes=True)
                
                tab_brand = Table(displayName="GPU_brand", ref="A1:B2")
                tab_brand.tableStyleInfo = style
                ref_sheet.add_table(tab_brand)
                
                tab_chipset = Table(displayName="Chipset_Table", ref="D1:E2")
                tab_chipset.tableStyleInfo = style
                ref_sheet.add_table(tab_chipset)
                
                tab_vram = Table(displayName="VRAM_table", ref="G1:H2")
                tab_vram.tableStyleInfo = style
                ref_sheet.add_table(tab_vram)
                
            if "GPU Lookup" not in wb.sheetnames:
                wb.create_sheet("GPU Lookup")
            sheet = wb["GPU Lookup"]
            
            if sheet.max_row == 1 and sheet.cell(row=1, column=1).value is None:
                sheet.append(["source", "raw_name", "original_price", "discount_price", "url", "crawled_date", "brand", "chipset", "vram_gb"])
                
            for item in self.data:
                row_idx = sheet.max_row + 1
                b_cell = f"B{row_idx}"
                
                brand_formula = f'=TEXTJOIN(",",TRUE,IF(COUNTIF({b_cell},"*"&GPU_brand[GPU brand text]&"*"),GPU_brand[GPU brand],""))'
                chipset_formula = f'=IFERROR(INDEX(Chipset_Table[Chipset], MATCH(TRUE, ISNUMBER( SEARCH(Chipset_Table[Chipset text],{b_cell})), 0)), "")'
                vram_formula = f'=TEXTJOIN(",",TRUE,IF(COUNTIF({b_cell},"*"&VRAM_table[Video memory text]&"*"),VRAM_table[Video memory],""))'
                
                row_data = [
                    item.get("source", ""),
                    item.get("raw_name", ""),
                    item.get("original_price", ""),
                    item.get("discount_price", ""),
                    item.get("url", ""),
                    crawled_date_str,
                    brand_formula,
                    chipset_formula,
                    vram_formula
                ]
                sheet.append(row_data)
                
            wb.save(excel_path)
            await self.send_telegram_alert(f"Thành công: Đã lấy được {len(self.data)} sản phẩm và lưu vào file Excel.")
            print(f"Data saved to {excel_path}")
            
        except PermissionError:
            await self.send_telegram_alert(f"Lỗi Permission Denied: Vui lòng đóng file {excel_path} trước khi chạy script.")
            print(f"Lỗi Permission Denied: Vui lòng đóng file {excel_path} trước khi chạy script.")
        except Exception as e:
            await self.send_telegram_alert(f"Lỗi khi lưu file Excel: {e}")
            print(f"Error saving to Excel: {e}")

    def run(self):
        asyncio.run(self.async_run())

if __name__ == "__main__":
    scraper = VGAScraper()
    scraper.run()
