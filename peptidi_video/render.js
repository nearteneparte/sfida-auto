// Renders peptidi.html frame by frame and pipes PNGs to ffmpeg.
// Usage: node render.js <lang> <out.mp4> [stillTimes...]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
(async () => {
  const [lang = 'en', out = `peptidi_${lang}.mp4`, ...stills] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto('file://' + path.resolve(__dirname, 'peptidi.html') + `?render=1&lang=${lang}`);
  await page.evaluate(() => window.ready);
  const canvas = await page.$('canvas');
  if (stills.length) {
    for (const s of stills) {
      await page.evaluate(t => window.render(t), parseFloat(s));
      await canvas.screenshot({ path: `still_${lang}_${s}.png` });
    }
    await browser.close();
    return;
  }
  const fps = 30, total = 30 * fps;
  const ff = spawn('ffmpeg', ['-y', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'slow', '-movflags', '+faststart', out],
    { stdio: ['pipe', 'ignore', 'inherit'] });
  for (let f = 0; f < total; f++) {
    await page.evaluate(t => window.render(t), f / fps);
    const buf = await canvas.screenshot({ type: 'png' });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
})();
