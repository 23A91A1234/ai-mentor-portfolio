import streamlit as st
from google import genai
from google.genai import types
import json

st.set_page_config(page_title='Résumé Scorer', layout='wide')
st.title('Résumé vs JD Fit Scorer')
st.caption('Day 5 Lab 5A — Free tools end-to-end')

col1, col2 = st.columns(2)
with col1:
    resume = st.text_area('Paste résumé', height=400)
with col2:
    jd = st.text_area('Paste job description', height=400)

api_key = st.secrets.get('GEMINI_API_KEY', None) or st.text_input('Gemini API key', type='password', help='Free key from aistudio.google.com')

if st.button('Score') and resume and jd and api_key:
    with st.spinner('Scoring...'):
        try:
            client = genai.Client(api_key=api_key)
            
            # Feature A & B: Prompt updated to ask for sub-scores AND learning resources
            prompt = f"""You are a placement coach. Given this résumé and JD, analyze the fit.
You must return a valid JSON object containing exactly the keys listed below. Do not include markdown formatting or code blocks.

Expected JSON Structure:
{{
  "score": int 0-100,
  "technical_skills_match": int 0-100,
  "soft_skills_match": int 0-100,
  "experience_relevance": int 0-100,
  "project_fit": int 0-100,
  "rationale": "string summary",
  "missing_skills": ["string"],
  "learning_resources": [
    {{
      "skill": "string name of skill",
      "resource_type": "YouTube Channel or Free Course",
      "link": "suggested platform name or placeholder link"
    }}
  ],
  "suggestions": ["string"]
}}

Résumé:
{resume}

JD:
{jd}"""

            resp = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            result = json.loads(resp.text)
            
            # UI: Score Metric
            st.metric('Fit Score', f"{result.get('score', 0)}/100")
            
            # Feature A: Score Breakdown
            st.subheader('Score Breakdown')
            chart_data = {
                "Technical Skills": result.get("technical_skills_match", 0),
                "Soft Skills": result.get("soft_skills_match", 0),
                "Experience Relevance": result.get("experience_relevance", 0),
                "Project Fit": result.get("project_fit", 0)
            }
            st.bar_chart(chart_data)
            
            # Content Columns
            st.subheader('Rationale')
            st.write(result.get('rationale', ''))
            
            st.subheader('Missing Skills')
            for s in result.get('missing_skills', []):
                st.write(f'- {s}')
                
            # Feature B: Top 3 Missing Skills with Learning Resources
            st.subheader('💡 Top 3 Missing Skills with Learning Resources')
            resources = result.get('learning_resources', [])
            if resources:
                for res in resources[:3]:  # Limit to top 3
                    with st.expander(f"📚 {res.get('skill')}"):
                        st.write(f"**Resource Type:** {res.get('resource_type')}")
                        st.write(f"**Recommended Source:** {res.get('link')}")
            else:
                st.write("No missing skills tracked or resources needed!")

            st.subheader('Suggestions for Improvement')
            for s in result.get('suggestions', []):
                st.write(f'- {s}')
                
        except json.JSONDecodeError:
            st.error("Failed to parse response. Output structure variant captured:")
            st.code(resp.text)
        except Exception as e:
            st.error(f"Execution Error: {e}")