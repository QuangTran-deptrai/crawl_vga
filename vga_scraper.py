import os
import re
import json
import asyncio
import pandas as pd
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from playwright.async_api import async_playwright
import httpx

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

    def process_with_ollama(self, df):
        print("Processing data with local Ollama (Gemma 2B)...")
        
        unique_names = df['raw_name'].unique().tolist()
        results_map = {}
        
        batch_size = 15
        
        system_prompt = (
            "Bạn là một chuyên gia phần cứng máy tính. Hãy phân tích chuỗi văn bản tên VGA và trả về JSON với cấu trúc là một JSON object chứa khóa 'items', "
            "với giá trị là một mảng (array) các object tương ứng với mỗi sản phẩm đầu vào. Mỗi object trong mảng bắt buộc phải gồm 5 trường: "
            "brand (thương hiệu, vd: ASUS, GIGABYTE, MSI...), chipset (ví dụ: RTX 4090, RX 7900 XTX...), vram_gb (số lượng VRAM, ví dụ: 24), vram_type (ví dụ: GDDR6X), raw_name (trường này chứa đúng tên gốc của sản phẩm đầu vào để map dữ liệu). "
            "Lưu ý: Bắt buộc trả về định dạng JSON object, đảm bảo mảng 'items' có số lượng phần tử bằng đúng số lượng tên đầu vào, không giải thích gì thêm."
        )

        for i in range(0, len(unique_names), batch_size):
            batch = unique_names[i:i+batch_size]
            prompt = "Phân tích các tên sau:\n" + "\n".join(batch)
            
            try:
                with httpx.Client(timeout=120.0) as client:
                    response = client.post(
                        "http://localhost:11434/api/chat",
                        json={
                            "model": "gemma2:2b",
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": prompt}
                            ],
                            "format": "json",
                            "stream": False,
                            "options": {
                                "temperature": 0.0
                            }
                        }
                    )
                
                if response.status_code == 200:
                    content = response.json().get('message', {}).get('content', '')
                    
                    try:
                        parsed_json = json.loads(content)
                        item_list = parsed_json.get('items', [])
                        
                        if not item_list and isinstance(parsed_json, dict):
                             for k, v in parsed_json.items():
                                 if isinstance(v, list):
                                     item_list = v
                                     break
                        elif not item_list and isinstance(parsed_json, list):
                             item_list = parsed_json
                             
                        for item in item_list:
                            if 'raw_name' in item:
                                results_map[item['raw_name']] = item
                                
                        print(f"Batch processed: {len(item_list)}/{len(batch)} items parsed from Ollama.")
                                
                    except json.JSONDecodeError:
                        print("Could not parse JSON from Ollama for batch")
                else:
                    print(f"Ollama API returned status {response.status_code}")
                    
            except Exception as e:
                print(f"Error calling Ollama API: {e}. Is Ollama running?")
                
        df['brand'] = df['raw_name'].apply(lambda x: results_map.get(x, {}).get('brand', ''))
        df['chipset'] = df['raw_name'].apply(lambda x: results_map.get(x, {}).get('chipset', ''))
        df['vram_gb'] = df['raw_name'].apply(lambda x: results_map.get(x, {}).get('vram_gb', ''))
        df['vram_type'] = df['raw_name'].apply(lambda x: results_map.get(x, {}).get('vram_type', ''))
        
        return df

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

        df = pd.DataFrame(self.data)
        
        df = self.process_with_ollama(df)
        
        vn_tz = timezone(timedelta(hours=7))
        df['crawled_date'] = datetime.now(vn_tz).strftime("%d/%m/%Y %H:%M:%S")
        
        csv_path = "vga_data.csv"
        file_exists = os.path.isfile(csv_path)
        
        try:
            df.to_csv(csv_path, mode='a', header=not file_exists, index=False, encoding='utf-8-sig')
            await self.send_telegram_alert(f"Thành công: Đã lấy được {len(self.data)} sản phẩm.")
            print(f"Data saved to {csv_path}")
        except Exception as e:
            await self.send_telegram_alert(f"Lỗi khi lưu file CSV: {e}")
            print(f"Error saving to CSV: {e}")

    def run(self):
        asyncio.run(self.async_run())

if __name__ == "__main__":
    scraper = VGAScraper()
    scraper.run()
