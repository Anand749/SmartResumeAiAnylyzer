import re
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
import logging
import PyPDF2
from docx import Document
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DocumentType:
    name: str
    keywords: List[str]
    threshold: float = 0.15

@dataclass
class ResumeSection:
    name: str
    keywords: List[str]
    weight: float = 1.0

@dataclass
class AnalysisResult:
    ats_score: float
    document_type: str
    keyword_match: Dict[str, any]
    section_score: float
    format_score: float
    suggestions: List[str]
    personal_info: Dict[str, str]
    education: List[str]
    experience: List[str]
    projects: List[str]
    skills: List[str]
    summary: str

class ResumeAnalyzer:
    def __init__(self):
        self.document_types = [
            DocumentType(
                'resume',
                [
                    'experience', 'education', 'skills', 'work', 'project', 
                    'objective', 'summary', 'employment', 'qualification', 
                    'achievements'
                ],
                0.15
            ),
            DocumentType(
                'marksheet',
                [
                    'grade', 'marks', 'score', 'semester', 'cgpa', 'sgpa', 
                    'examination', 'result', 'academic year', 'percentage'
                ]
            ),
            DocumentType(
                'certificate',
                [
                    'certificate', 'certification', 'awarded', 'completed', 
                    'achievement', 'training', 'course completion', 'qualified'
                ]
            ),
            DocumentType(
                'id_card',
                [
                    'id card', 'identity', 'student id', 'employee id', 
                    'valid until', 'date of issue', 'identification'
                ]
            )
        ]
        
        self.essential_sections = [
            ResumeSection(
                'contact',
                ['email', 'phone', 'address', 'linkedin', 'github'],
                0.2
            ),
            ResumeSection(
                'education',
                ['education', 'university', 'college', 'degree', 'academic'],
                0.2
            ),
            ResumeSection(
                'experience',
                ['experience', 'work', 'employment', 'job', 'internship'],
                0.3
            ),
            ResumeSection(
                'skills',
                ['skills', 'technologies', 'tools', 'proficiencies', 'expertise'],
                0.2
            ),
            ResumeSection(
                'summary',
                ['summary', 'objective', 'profile', 'about'],
                0.1
            )
        ]
        
        self.contact_patterns = {
            'email': r'\b[\w\.-]+@[\w\.-]+\.\w+\b',
            'phone': r'(\+\d{1,3}[-.]?)?\s*\(?\d{3}\)?[-.]?\s*\d{3}[-.]?\s*\d{4}',
            'linkedin': r'linkedin\.com/in/[\w-]+',
            'github': r'github\.com/[\w-]+'
        }

    def detect_document_type(self, text: str) -> str:
        """Detect the type of document based on keyword analysis."""
        text = text.lower()
        scores = {}
        
        for doc_type in self.document_types:
            matches = sum(1 for keyword in doc_type.keywords if keyword in text)
            density = matches / len(doc_type.keywords)
            frequency = matches / (len(text.split()) + 1)
            scores[doc_type.name] = (density * 0.7) + (frequency * 0.3)
        
        best_match = max(scores.items(), key=lambda x: x[1])
        return best_match[0] if best_match[1] > self.document_types[0].threshold else 'unknown'

    def _extract_with_regex(self, text: str, pattern: str) -> Optional[str]:
        """Helper method to extract information using regex."""
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(0) if match else None

    def extract_personal_info(self, text: str) -> Dict[str, str]:
        """Extract personal information from resume text."""
        info = {
            'name': '',
            'email': '',
            'phone': '',
            'linkedin': '',
            'github': '',
            'portfolio': ''
        }
        
        # Extract name from first non-empty line
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            info['name'] = lines[0]
        
        # Extract contact info using regex patterns
        for field, pattern in self.contact_patterns.items():
            info[field] = self._extract_with_regex(text, pattern) or ''
        
        return info

    def _extract_section(self, text: str, section_keywords: List[str]) -> List[str]:
        """Generic method to extract a section based on keywords."""
        lines = text.split('\n')
        section_content = []
        in_section = False
        current_entry = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_entry:
                    section_content.append(' '.join(current_entry))
                    current_entry = []
                continue
                
            # Check if we're entering the section
            if not in_section and any(keyword.lower() in line.lower() 
                                    for keyword in section_keywords):
                in_section = True
                current_entry.append(line)
                continue
                
            if in_section:
                # Check if we're leaving the section
                if any(section.keywords[0].lower() in line.lower() 
                       for section in self.essential_sections 
                       if section.keywords[0].lower() not in section_keywords[0].lower()):
                    in_section = False
                    if current_entry:
                        section_content.append(' '.join(current_entry))
                        current_entry = []
                    continue
                    
                current_entry.append(line)
        
        if current_entry:
            section_content.append(' '.join(current_entry))
            
        return section_content

    def extract_education(self, text: str) -> List[str]:
        """Extract education information from resume text."""
        return self._extract_section(text, ['education', 'academic'])

    def extract_experience(self, text: str) -> List[str]:
        """Extract work experience information from resume text."""
        return self._extract_section(text, ['experience', 'work'])

    def extract_projects(self, text: str) -> List[str]:
        """Extract project information from resume text."""
        return self._extract_section(text, ['projects', 'project'])

    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text."""
        skills_section = self._extract_section(text, ['skills', 'technical skills'])
        skills = set()
        separators = [',', '•', '|', '/', '\\', '·', '>', '-', '–', '―']
        
        for item in skills_section:
            for sep in separators:
                if sep in item:
                    skills.update(skill.strip() for skill in item.split(sep) if skill.strip())
        
        return list(skills)

    def extract_summary(self, text: str) -> str:
        """Extract summary/objective from resume text."""
        summary_section = self._extract_section(text, ['summary', 'objective'])
        return ' '.join(summary_section) if summary_section else ''

    def calculate_keyword_match(self, resume_text: str, required_skills: List[str]) -> Dict[str, any]:
        """Calculate how well the resume matches required skills."""
        if not required_skills:
            return {
                'score': 0,
                'found_skills': [],
                'missing_skills': []
            }
            
        resume_text = resume_text.lower()
        found_skills = []
        
        for skill in required_skills:
            skill_lower = skill.lower()
            # Check for exact or partial match
            if (skill_lower in resume_text or 
                any(skill_lower in phrase for phrase in resume_text.split('.'))):
                found_skills.append(skill)
                
        match_score = (len(found_skills) / len(required_skills)) * 100
        missing_skills = [skill for skill in required_skills if skill not in found_skills]
        
        return {
            'score': match_score,
            'found_skills': found_skills,
            'missing_skills': missing_skills
        }

    def check_resume_sections(self, text: str) -> float:
        """Check completeness of essential resume sections."""
        text = text.lower()
        section_scores = {}
        
        for section in self.essential_sections:
            found = sum(1 for keyword in section.keywords if keyword in text)
            section_scores[section.name] = (found / len(section.keywords)) * section.weight * 100
            
        return sum(section_scores.values())

    def check_formatting(self, text: str) -> Tuple[float, List[str]]:
        """Evaluate resume formatting quality."""
        lines = text.split('\n')
        score = 100
        deductions = []
        
        # Content length check
        if len(text) < 300:
            score -= 30
            deductions.append("Resume is too short (less than 300 characters)")
            
        # Section headers check
        if not any(line.strip().isupper() for line in lines):
            score -= 20
            deductions.append("No clear section headers (all caps) found")
            
        # Bullet points check
        if not any(line.strip().startswith(('•', '-', '*', '→')) for line in lines):
            score -= 20
            deductions.append("No bullet points found for listing details")
            
        # Spacing consistency check
        if any(not line.strip() and not next_line.strip() 
               for line, next_line in zip(lines[:-1], lines[1:])):
            score -= 15
            deductions.append("Inconsistent spacing between sections")
            
        # Contact information check
        if not any(re.search(pattern, text) for pattern in self.contact_patterns.values()):
            score -= 15
            deductions.append("Missing or improperly formatted contact information")
            
        return max(0, score), deductions

    def extract_text_from_pdf(self, file) -> str:
        """Extract text from PDF file."""
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(file.read()))
            return "\n".join(page.extract_text() for page in pdf_reader.pages)
        except Exception as e:
            logger.error(f"PDF extraction error: {str(e)}")
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")

    def extract_text_from_docx(self, file) -> str:
        """Extract text from DOCX file."""
        try:
            doc = Document(BytesIO(file.read()))
            return "\n".join(para.text for para in doc.paragraphs if para.text.strip())
        except Exception as e:
            logger.error(f"DOCX extraction error: {str(e)}")
            raise ValueError(f"Failed to extract text from DOCX: {str(e)}")

    def analyze_resume(self, resume_data: Dict[str, any], job_requirements: Dict[str, any]) -> AnalysisResult:
        """Comprehensive resume analysis with scoring and suggestions."""
        text = resume_data.get('raw_text', '')
        if not text:
            raise ValueError("No text content provided for analysis")
            
        # Document type detection
        doc_type = self.detect_document_type(text)
        if doc_type != 'resume':
            return AnalysisResult(
                ats_score=0,
                document_type=doc_type,
                keyword_match={'score': 0, 'found_skills': [], 'missing_skills': []},
                section_score=0,
                format_score=0,
                suggestions=[f"This appears to be a {doc_type} document. Please upload a resume."],
                personal_info={},
                education=[],
                experience=[],
                projects=[],
                skills=[],
                summary=''
            )
            
        # Extract all resume content
        personal_info = self.extract_personal_info(text)
        education = self.extract_education(text)
        experience = self.extract_experience(text)
        projects = self.extract_projects(text)
        skills = self.extract_skills(text)
        summary = self.extract_summary(text)
        
        # Calculate scores
        keyword_match = self.calculate_keyword_match(text, job_requirements.get('required_skills', []))
        section_score = self.check_resume_sections(text)
        format_score, format_deductions = self.check_formatting(text)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(
            personal_info, education, experience, 
            projects, skills, summary, 
            keyword_match, format_deductions,
            job_requirements
        )
        
        # Calculate comprehensive ATS score
        ats_score = self._calculate_ats_score(
            personal_info, education, experience,
            skills, summary, keyword_match['score'],
            format_score
        )
        
        return AnalysisResult(
            ats_score=ats_score,
            document_type='resume',
            keyword_match=keyword_match,
            section_score=section_score,
            format_score=format_score,
            suggestions=suggestions,
            personal_info=personal_info,
            education=education,
            experience=experience,
            projects=projects,
            skills=skills,
            summary=summary
        )

    def _generate_suggestions(self, personal_info, education, experience, 
                            projects, skills, summary, 
                            keyword_match, format_deductions,
                            job_requirements) -> List[str]:
        """Generate improvement suggestions based on analysis."""
        suggestions = []
        
        # Contact info suggestions
        if not personal_info.get('email'):
            suggestions.append("Add a professional email address")
        if not personal_info.get('phone'):
            suggestions.append("Include a phone number")
        if not personal_info.get('linkedin'):
            suggestions.append("Add your LinkedIn profile URL")
            
        # Summary suggestions
        if not summary:
            suggestions.append("Add a professional summary highlighting your key qualifications")
        elif len(summary.split()) < 30:
            suggestions.append("Expand your professional summary to better showcase your experience")
            
        # Skills suggestions
        if not skills:
            suggestions.append("Add a dedicated skills section")
        elif keyword_match['score'] < 70:
            suggestions.append(f"Add missing skills: {', '.join(keyword_match['missing_skills'][:3])}")
            
        # Experience suggestions
        if not experience:
            suggestions.append("Add your work experience section")
        else:
            if not any(re.search(r'\b(19|20)\d{2}\b', exp) for exp in experience):
                suggestions.append("Include dates for each work experience")
            if not any(re.search(r'[•\-\*]', exp) for exp in experience):
                suggestions.append("Use bullet points to list achievements")
                
        # Education suggestions
        if not education:
            suggestions.append("Add your educational background")
        elif not any(re.search(r'\b(bachelor|master|phd|degree)\b', edu.lower()) 
                    for edu in education):
            suggestions.append("Specify your degree type")
            
        # Formatting suggestions
        suggestions.extend(format_deductions)
        
        return suggestions if suggestions else ["Your resume is well-optimized!"]

    def _calculate_ats_score(self, personal_info, education, experience,
                           skills, summary, keyword_score, 
                           format_score) -> float:
        """Calculate comprehensive ATS score with weighted components."""
        weights = {
            'contact': 0.15,
            'summary': 0.10,
            'skills': 0.25,
            'experience': 0.25,
            'education': 0.15,
            'format': 0.10
        }
        
        # Calculate component scores
        contact_score = 100 if all(personal_info.get(field) for field in ['email', 'phone']) else 50
        summary_score = 100 if summary and len(summary.split()) >= 30 else 50
        skills_score = keyword_score
        experience_score = 100 if experience else 50
        education_score = 100 if education else 50
        
        # Calculate weighted score
        weighted_score = (
            contact_score * weights['contact'] +
            summary_score * weights['summary'] +
            skills_score * weights['skills'] +
            experience_score * weights['experience'] +
            education_score * weights['education'] +
            format_score * weights['format']
        )
        
        return min(100, weighted_score)