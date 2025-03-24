from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
import jmcomic
import os
import time
from PIL import Image
import asyncio
import re

__plugin_meta__ = PluginMetadata(
    name="JM漫画下载",
    description="通过JM号下载本子并转换为PDF",
    usage="/jm  示例：/jm 123456",
    extra={"version": "1.0.2"}
)

jm_download = on_command("jm", aliases={"JM"}, priority=5, block=True)

async def all2PDF(input_folder: str, pdfpath: str, pdfname: str) -> str:
    """将图片文件夹转换为PDF"""
    start_time = time.time()
    pdf_file_path = ""
    
    try:
        image_paths = []
        for root, dirs, files in os.walk(input_folder):
            dirs.sort(key=lambda x: int(x) if x.isdigit() else 0)
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    full_path = os.path.join(root, file)
                    image_paths.append(full_path)

        if not image_paths:
            raise RuntimeError(f"目录 {input_folder} 中未找到图片文件")

        image_paths = sorted(image_paths, 
                           key=lambda x: [int(c) if c.isdigit() else c 
                                        for c in re.split(r'(\d+)', x)])

        images = []
        for img_path in image_paths:
            with Image.open(img_path) as img:
                if img.mode != "RGB":
                    img = img.convert("RGB")
                images.append(img.copy())

        pdf_file_path = os.path.join(pdfpath, f"{pdfname}.pdf")
        images[0].save(
            pdf_file_path,
            "PDF",
            save_all=True,
            append_images=images[1:],
            quality=95
        )

        print(f"PDF生成成功 | 耗时：{time.time()-start_time:.2f}秒")
        return pdf_file_path

    except Exception as e:
        if pdf_file_path and os.path.exists(pdf_file_path):
            os.remove(pdf_file_path)
        raise RuntimeError(f"PDF转换失败: {str(e)}")

def check_local_files(comic_path: str, pdf_path: str) -> int:
    """检查本地文件状态
    返回值: 
    0 - 需要重新下载
    1 - PDF已存在
    2 - 图片已存在
    """
    if os.path.exists(pdf_path):
        return 1
    
    if os.path.exists(comic_path) and any(
        f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')) 
        for f in os.listdir(comic_path)
    ):
        return 2
    
    return 0

@jm_download.handle()
async def handle_jm(event: GroupMessageEvent, bot: Bot, args=CommandArg()):
    comic_id = args.extract_plain_text().strip()

    try:
        config_path = os.path.join(os.path.dirname(__file__), "config.yml")
        option = jmcomic.JmOption.from_file(config_path)
        option.dir_rule.rule = "Bd_Aid"
        base_dir = option.dir_rule.base_dir
    except Exception as e:
        await jm_download.finish(f"❌ 配置错误: {str(e)}")
        return

    comic_path = os.path.join(base_dir, comic_id)
    pdf_path = os.path.join(base_dir, f"{comic_id}.pdf")

    # 检查本地文件状态
    file_status = check_local_files(comic_path, pdf_path)
    
    # 如果PDF已存在直接上传
    if file_status == 1:
        try:
            await bot.call_api(
                'upload_group_file',
                group_id=event.group_id,
                file=pdf_path,
                name=f"{comic_id}.pdf"
            )
            await jm_download.finish()
        except Exception as e:
            await jm_download.finish(f"❌ 上传失败: {str(e)}")
        return

    # 如果图片已存在跳过下载
    if file_status == 2:
        await jm_download.send("🔄 检测到本地已存在图片文件，跳过下载...")
    else:
        try:
            await jm_download.send(f"🔄 开始下载JM{comic_id}...")
            await asyncio.to_thread(jmcomic.download_album, comic_id, option)
            
            if not os.path.exists(comic_path) or len(os.listdir(comic_path)) == 0:
                raise RuntimeError("下载目录为空，可能ID无效")
                
        except Exception as e:
            await jm_download.finish(f"❌ 下载失败: {str(e)}")
            return

    # 转换PDF
    try:
        await jm_download.send("🔄 转换PDF中...")
        pdf_path = await all2PDF(comic_path, base_dir, comic_id)
    except Exception as e:
        await jm_download.finish(f"❌ {str(e)}")
        return

    # 上传PDF
    try:
        await bot.call_api(
            'upload_group_file',
            group_id=event.group_id,
            file=pdf_path,
            name=f"{comic_id}.pdf"
        )
    except Exception as e:
        await jm_download.finish(f"❌ 上传失败: {str(e)}")
    finally:
        # 无论成功与否都保留所有文件
        await jm_download.finish()