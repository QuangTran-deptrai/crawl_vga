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
import google.generativeai as genai

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

    def load_regex_rules(self, excel_path="vga_data.xlsx"):
        brand_rules = {}
        chipset_rules = {}
        vram_rules = {}
        if os.path.exists(excel_path):
            try:
                df = pd.read_excel(excel_path, sheet_name='GPU ref', engine='openpyxl')
                if 'GPU brand text' in df.columns and 'GPU brand' in df.columns:
                    for text, val in zip(df['GPU brand text'], df['GPU brand']):
                        if pd.notna(text) and pd.notna(val):
                            brand_rules[str(text).strip()] = str(val).strip()
                if 'Chipset text' in df.columns and 'Chipset' in df.columns:
                    for text, val in zip(df['Chipset text'], df['Chipset']):
                        if pd.notna(text) and pd.notna(val):
                            chipset_rules[str(text).strip()] = str(val).strip()
                if 'Video memory text' in df.columns and 'Video memory' in df.columns:
                    for text, val in zip(df['Video memory text'], df['Video memory']):
                        if pd.notna(text) and pd.notna(val):
                            vram_rules[str(text).strip()] = str(val).strip()
            except Exception as e:
                print(f"Error loading GPU ref: {e}")
        return brand_rules, chipset_rules, vram_rules

    def get_matches(self, text, rules_dict):
        text_upper = text.upper()
        
        # Tìm tất cả vị trí match trong text
        found = []  # [(start, end, key, value)]
        for key, val in rules_dict.items():
            key_upper = key.upper()
            start = 0
            while True:
                pos = text_upper.find(key_upper, start)
                if pos == -1:
                    break
                found.append((pos, pos + len(key_upper), key_upper, val))
                start = pos + 1
        
        # Sắp xếp: dài nhất trước, nếu bằng nhau thì vị trí sớm hơn trước
        found.sort(key=lambda x: (-(x[1] - x[0]), x[0]))
        
        # Loại bỏ các match bị overlap bởi match dài hơn
        kept = []
        for item in found:
            s, e, k, v = item
            is_overlapped = False
            for ks, ke, kk, kv in kept:
                # Nếu match hiện tại nằm gọn trong hoặc overlap với match đã giữ
                if s >= ks and e <= ke:
                    is_overlapped = True
                    break
                # Overlap một phần: match hiện tại bắt đầu trong match đã giữ
                if ks <= s < ke or ks < e <= ke:
                    is_overlapped = True
                    break
            if not is_overlapped:
                kept.append(item)
        
        # Trả về danh sách value duy nhất
        return list(set(v for _, _, _, v in kept))

    async def process_ambiguous_with_gemini(self, items_batch):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("No GEMINI_API_KEY found, skipping AI processing.")
            return []
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
        
        prompt = "Extract brand, chipset, and vram_gb for the following GPU names. Return a JSON array of objects with keys: id, brand, chipset, vram_gb. If not found, return empty string.\n\n"
        prompt += json.dumps([{"id": item['id'], "raw_name": item['raw_name']} for item in items_batch], ensure_ascii=False)
        
        try:
            response = await model.generate_content_async(prompt)
            return json.loads(response.text)
        except Exception as e:
            print(f"Gemini API error: {e}")
            return []

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
                
            brand_rules, chipset_rules, vram_rules = self.load_regex_rules(excel_path)
            
            ambiguous_items = []
            for idx, item in enumerate(self.data):
                item['id'] = idx
                item['is_ambiguous'] = False
                if brand_rules or chipset_rules or vram_rules:
                    b_matches = self.get_matches(item['raw_name'], brand_rules)
                    c_matches = self.get_matches(item['raw_name'], chipset_rules)
                    v_matches = self.get_matches(item['raw_name'], vram_rules)
                    if len(b_matches) > 1 or len(c_matches) > 1 or len(v_matches) > 1:
                        item['is_ambiguous'] = True
                        ambiguous_items.append(item)

            ai_results = {}
            if ambiguous_items:
                batch_size = 20
                for i in range(0, len(ambiguous_items), batch_size):
                    batch = ambiguous_items[i:i+batch_size]
                    res = await self.process_ambiguous_with_gemini(batch)
                    for r in res:
                        ai_results[r.get('id')] = r
                    if i + batch_size < len(ambiguous_items):
                        await asyncio.sleep(2)

            for item in self.data:
                row_idx = sheet.max_row + 1
                b_cell = f"B{row_idx}"
                
                if item['is_ambiguous'] and item['id'] in ai_results:
                    # Nhập nhằng (>1 kết quả) → dùng kết quả AI
                    ai_data = ai_results[item['id']]
                    brand_val = ai_data.get('brand', '')
                    chipset_val = ai_data.get('chipset', '')
                    vram_val = ai_data.get('vram_gb', '')
                else:
                    # Regex trả đúng 1 kết quả → ghi text tĩnh
                    # Regex trả 0 kết quả → ghi công thức Excel để Excel tự tìm
                    b_matches = self.get_matches(item['raw_name'], brand_rules) if brand_rules else []
                    c_matches = self.get_matches(item['raw_name'], chipset_rules) if chipset_rules else []
                    v_matches = self.get_matches(item['raw_name'], vram_rules) if vram_rules else []
                    
                    brand_val = b_matches[0] if len(b_matches) == 1 else f'=_xlfn.TEXTJOIN(",",TRUE,_xlfn._xlws.FILTER(GPU_brand[GPU brand], (GPU_brand[GPU brand text]<>"") * ISNUMBER(SEARCH(GPU_brand[GPU brand text], {b_cell})), ""))'
                    chipset_val = c_matches[0] if len(c_matches) == 1 else f'=_xlfn.TEXTJOIN(",",TRUE,_xlfn._xlws.FILTER(Chipset_Table[Chipset], (Chipset_Table[Chipset text]<>"") * ISNUMBER(SEARCH(Chipset_Table[Chipset text], {b_cell})), ""))'
                    vram_val = v_matches[0] if len(v_matches) == 1 else f'=_xlfn.TEXTJOIN(",",TRUE,_xlfn._xlws.FILTER(VRAM_table[Video memory], (VRAM_table[Video memory text]<>"") * ISNUMBER(SEARCH(VRAM_table[Video memory text], {b_cell})), ""))'
                
                row_data = [
                    item.get("source", ""),
                    item.get("raw_name", ""),
                    item.get("original_price", ""),
                    item.get("discount_price", ""),
                    item.get("url", ""),
                    crawled_date_str,
                    brand_val,
                    chipset_val,
                    vram_val
                ]
                sheet.append(row_data)
                
            table_name = "GPU_Lookup_Data"
            table_ref = f"A1:I{sheet.max_row}"
            existing_table = None
            for tbl in sheet.tables.values():
                if tbl.displayName == table_name:
                    existing_table = tbl
                    break
            if existing_table:
                existing_table.ref = table_ref
            else:
                lookup_tab = Table(displayName=table_name, ref=table_ref)
                style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False, showLastColumn=False, showRowStripes=True, showColumnStripes=True)
                lookup_tab.tableStyleInfo = style
                sheet.add_table(lookup_tab)
                
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
