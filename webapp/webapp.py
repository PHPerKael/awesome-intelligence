import os
from pathlib import Path
import logging
import gradio as gr
from frontend.submit import ask_rag

def init_logging():
    """全局日志初始化函数"""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # 根日志配置
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)


gradio_tmp_dir = Path(os.getenv("GRADIO_TEMP_DIR"))

# 构建界面
with gr.Blocks(title="智能文档助手") as demo:
    gr.Markdown("# 🚀 企业级文档智能分析系统")
    
    with gr.Row():
        files_upload = gr.File(
            label="上传技术文档",
            file_types=[".txt",".md",".pdf",".docx",".pptx",".xlsx",".md",".json",".csv",".mp3",".wav",".png",".jpg"],
            file_count="multiple",
        )

        question = gr.Textbox(
            label="输入问题", 
            placeholder="输入与技术文档相关的问题，例如：\n• Kubernetes 资源配额如何配置\n• 如何优化 Spark 任务调度",
            lines=4
        )

    # 新增已上传文件预览
    with gr.Accordion("已上传文件", open=False):
        file_preview = gr.DataFrame(
            headers=["文件名", "大小", "状态"],
            interactive=False
        )

    with gr.Row():
        submit_btn = gr.Button("开始分析", variant="primary")
        # clear_btn = gr.Button("清空输入")
    
    output = gr.Markdown(label="分析结果", latex_delimiters=[])
    
    # 事件绑定
    submit_btn.click(
        fn=ask_rag,
        inputs=[files_upload, question],
        outputs=output
    )
    # clear_btn.click(
    #     inputs=[files_upload, question, output],
    #     outputs=[files_upload, question, output]
    # )

if __name__ == "__main__":
    init_logging()
    # 启动服务
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("SERVER_PORT", 7860)),
        show_error=True,
        allowed_paths=[gradio_tmp_dir.absolute()],
    )