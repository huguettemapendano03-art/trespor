
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://127.0.0.1:5000/login');
  await page.fill('input[name="username"]', 'admin');
  await page.fill('input[name="password"]', 'admin123');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(1000);
  await page.click('#btn-tab-visual');
  await page.waitForTimeout(1000);
  await page.screenshot({ path: 'bulletin_web_screenshot.png', fullPage: true });
  await browser.close();
})();
