"""
文件上传 — UploadFile + File() 参数
返回文件名、大小、类型
"""

from fastapi import FastAPI, File, UploadFile

app = FastAPI(title="文件上传示例")


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    上传单个文件，返回文件信息：
    - filename:  文件名
    - size:      文件大小（字节）
    - content_type:  MIME 类型
    """
    # 读取文件内容到内存以计算大小
    contents = await file.read()
    size = len(contents)

    return {
        "filename": file.filename,
        "size": size,
        "content_type": file.content_type,
    }


@app.get("/")
def root():
    return {
        "msg": "请使用 POST /upload 上传文件（表单字段名: file）"
    }


# 运行入口
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("day53_upload:app", host="127.0.0.1", port=8000, reload=True)
