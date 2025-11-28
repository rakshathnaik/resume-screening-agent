import gradio as gr
import google.generativeai as genai
import PyPDF2 as pdf
import os

# --- 1. SETUP API KEY ---
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("⚠️ Google API Key not found! Check Settings > Secrets.")

genai.configure(api_key=api_key)

# --- 2. PDF EXTRACTION ---
def input_pdf_text(file_obj):
    if file_obj is None:
        return ""
    try:
        reader = pdf.PdfReader(file_obj.name)
        text = ""
        for page in range(len(reader.pages)):
            page = reader.pages[page]
            text += str(page.extract_text())
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

# --- 3. AI ANALYSIS (Stylish Output) ---
def analyze_resume(job_description, pdf_file):
    if not pdf_file or not job_description:
        return "⚠️ Please provide both a Job Description and a Resume."
    
    resume_text = input_pdf_text(pdf_file)
    
    # Updated Prompt for Stylish Formatting
    prompt_template = f"""
    Act Like a skilled ATS (Application Tracking System).
    Evaluate the resume based on the given job description.
    
    JOB DESCRIPTION:
    {job_description}
    
    RESUME TEXT:
    {resume_text}
    
    OUTPUT FORMAT (Markdown):
    1. Start with a header "## 📊 ATS Evaluation Report".
    2. Then, show the Match Percentage prominently (e.g., "### 🎯 Match Score: 85%").
    3. List missing keywords using bullet points with an emoji (e.g., "❌ Keyword").
    4. Provide a profile summary under "### 📝 Profile Summary".
    5. Use Bold text (**text**) for emphasis.
    """
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash') 
        response = model.generate_content(prompt_template)
        return response.text
    except Exception as e:
        return f"⚠️ API Error: {str(e)}"

# --- 4. UI LAYOUT ---
# We removed the 'theme' argument to prevent the error you saw earlier
with gr.Blocks(title="AI Resume Screener") as demo:
    gr.Markdown("# 🤖 AI Resume Screening Agent")
    gr.Markdown("Paste a Job Description and upload a Resume to get an ATS score.")
    
    with gr.Row():
        with gr.Column():
            jd_input = gr.Textbox(lines=8, label="Job Description", placeholder="Paste Job Description Here...")
            resume_input = gr.File(label="Upload Resume (PDF)", file_types=[".pdf"])
            submit_btn = gr.Button("Analyze Resume", variant="primary")
        
        with gr.Column():
            # CHANGED: 'Textbox' -> 'Markdown' to render the bold text and headers nicely
            output_box = gr.Markdown(label="Analysis Result")
    
    submit_btn.click(fn=analyze_resume, inputs=[jd_input, resume_input], outputs=output_box)

# Launch
demo.launch()
