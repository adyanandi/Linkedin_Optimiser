import google.generativeai as genai

genai.configure(api_key="AIzaSyDJoH-MeUqwI-GBhH_u0NlZXEcKRW-wWOQ")

def analyze_linkedin_profile(profile_data):
    """
    Analyzes a LinkedIn profile using Gemini AI and provides insights.
    
    Args:
        profile_data (dict): Scraped LinkedIn profile data.
    
    Returns:
        str: AI-generated insights.
    """
    # Format the profile data into a structured text prompt
    profile_text = "\n".join([f"**{key}:** {value}" for key, value in profile_data.items() if value])

    prompt = f"""
🔹 **Task:** Analyze this LinkedIn profile and provide **brief, impactful insights** for better visibility, job opportunities, and networking.  

### **🚀 Key Insights (Keep it short & direct):**  
✅ **Profile Score (Out of 10)** – Rate & justify in 1 line.  
✅ **Top 3 Strengths** – Bullet points, 1 line each.  
✅ **Top 3 Fixes** – Clear & actionable, 1 line each.  
✅ **Best Job Roles & Networking Tips** – 2-3 concise suggestions.  

🔹 **Profile Data:**  
{profile_text}  

💡 **Keep it crisp!** No long paragraphs—just **quick takeaways**.
"""

    # Send request to Gemini AI
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)
    
    return response.text


