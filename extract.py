"""
SwiftVisa - Milestone 1: Extract Data from Raw Sources
Extracts visa policy information from PDFs, Word documents, and text files
Outputs ALL data into ONE consolidated file

Author: [Your Name]
Date: 2026
Milestone: 1 - Knowledge Base Creation
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime


class RawDataExtractor:
    """Extract visa policy data from multiple raw source formats"""
    
    def __init__(self, 
                 input_dir: str = "data/raw",
                 consolidated_output: str = "data/all_extracted_policies.json"):
        self.input_dir = Path(input_dir)
        self.consolidated_output = Path(consolidated_output)
        
        # Create output directory
        self.consolidated_output.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 Raw Input: {self.input_dir}")
        print(f"📄 Consolidated Output: {self.consolidated_output}")
    
    def extract_from_txt(self, file_path: Path) -> str:
        """Extract text from .txt files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            return ""
    
    def extract_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF files (requires PyPDF2)"""
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except ImportError:
            print(f"⚠️  PyPDF2 not installed. Install with: pip install PyPDF2")
            return ""
        except Exception as e:
            print(f"❌ Error reading PDF {file_path}: {e}")
            return ""
    
    def extract_from_docx(self, file_path: Path) -> str:
        """Extract text from Word documents (requires python-docx)"""
        try:
            from docx import Document
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except ImportError:
            print(f"⚠️  python-docx not installed. Install with: pip install python-docx")
            return ""
        except Exception as e:
            print(f"❌ Error reading DOCX {file_path}: {e}")
            return ""
    
    def parse_policy_info(self, raw_text: str, filename: str) -> Dict:
        """Parse raw text into structured policy information"""
        # Extract country and visa type from filename
        parts = filename.replace('.txt', '').replace('.pdf', '').replace('.docx', '').split('_')
        
        if len(parts) >= 2:
            country = parts[0].replace('_', ' ').title()
            visa_type = parts[1].replace('_', ' ').title()
        else:
            country = "Unknown"
            visa_type = "Unknown"
        
        # Try to extract specific sections using regex
        requirements = self._extract_section(raw_text, r'REQUIREMENTS[:\s]*(.*?)(?=REQUIRED|PROCESSING|FEES|$)')
        documents = self._extract_section(raw_text, r'REQUIRED DOCUMENTS[:\s]*(.*?)(?=PROCESSING|FEES|$)')
        processing_time = self._extract_section(raw_text, r'PROCESSING TIME[:\s]*(.*?)(?=FEES|$)')
        fees = self._extract_section(raw_text, r'FEES[:\s]*(.*?)(?=\n\n|$)')
        
        # Create structured policy object
        policy_data = {
            "id": f"{country.replace(' ', '_')}_{visa_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "country": country,
            "visa_type": visa_type,
            "source_file": filename,
            "extraction_date": datetime.now().isoformat(),
            "content": {
                "requirements": self._clean_text(requirements),
                "required_documents": self._clean_text(documents),
                "processing_time": self._clean_text(processing_time),
                "fees": self._clean_text(fees),
                "full_text": raw_text
            },
            "metadata": {
                "extraction_method": "file_upload",
                "file_type": Path(filename).suffix,
                "character_count": len(raw_text),
                "word_count": len(raw_text.split())
            }
        }
        
        return policy_data
    
    def _extract_section(self, text: str, pattern: str) -> str:
        """Extract specific section from text using regex"""
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else ""
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return "Not specified"
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'[^\w\s.,;:!?-]', '', text)
        return text
    
    def process_all_files(self) -> List[Dict]:
        """Process all raw files and extract structured data"""
        all_policies = []
        
        # Find all supported files
        txt_files = list(self.input_dir.glob("*.txt"))
        pdf_files = list(self.input_dir.glob("*.pdf"))
        docx_files = list(self.input_dir.glob("*.docx"))
        
        all_files = txt_files + pdf_files + docx_files
        
        if not all_files:
            print(f"❌ No raw files found in {self.input_dir}")
            print("   Supported formats: .txt, .pdf, .docx")
            return all_policies
        
        print(f"\n📄 Found {len(all_files)} raw files")
        
        for file_path in all_files:
            print(f"\n📖 Extracting: {file_path.name}")
            
            # Extract based on file type
            if file_path.suffix == '.txt':
                raw_text = self.extract_from_txt(file_path)
            elif file_path.suffix == '.pdf':
                raw_text = self.extract_from_pdf(file_path)
            elif file_path.suffix == '.docx':
                raw_text = self.extract_from_docx(file_path)
            else:
                continue
            
            if not raw_text:
                continue
            
            # Parse into structured format
            policy_data = self.parse_policy_info(raw_text, file_path.name)
            all_policies.append(policy_data)
            
            print(f"   ✅ Extracted: {policy_data['country']} - {policy_data['visa_type']}")
        
        return all_policies
    
    def save_to_consolidated_json(self, policies: List[Dict]):
        """Save ALL extracted policies to ONE consolidated JSON file"""
        output_data = {
            "metadata": {
                "project": "SwiftVisa",
                "milestone": "Milestone 1 - Knowledge Base Creation",
                "extraction_date": datetime.now().isoformat(),
                "total_policies": len(policies),
                "countries": list(set(p['country'] for p in policies)),
                "visa_types": list(set(p['visa_type'] for p in policies)),
                "output_type": "Single Consolidated File"
            },
            "policies": policies
        }
        
        with open(self.consolidated_output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 ALL data saved to ONE file: {self.consolidated_output}")
    
    def generate_summary_report(self, policies: List[Dict]) -> Dict:
        """Generate summary report of extracted data"""
        country_count = {}
        visa_type_count = {}
        total_chars = 0
        
        for policy in policies:
            country = policy['country']
            visa_type = policy['visa_type']
            
            country_count[country] = country_count.get(country, 0) + 1
            visa_type_count[visa_type] = visa_type_count.get(visa_type, 0) + 1
            total_chars += policy['metadata']['character_count']
        
        summary = {
            "total_policies": len(policies),
            "countries": country_count,
            "visa_types": visa_type_count,
            "total_characters": total_chars,
            "average_characters_per_policy": total_chars // len(policies) if policies else 0,
            "extraction_date": datetime.now().isoformat()
        }
        
        return summary


def main():
    """Main entry point for raw data extraction"""
    print("=" * 70)
    print("SWIFTVISA - MILESTONE 1: EXTRACT DATA (SINGLE CONSOLIDATED FILE)")
    print("=" * 70)
    
    extractor = RawDataExtractor(
        input_dir="data/raw",
        consolidated_output="data/all_extracted_policies.json"
    )
    
    # Process all files
    policies = extractor.process_all_files()
    
    if not policies:
        print("\n⚠️  No policies extracted. Please add files to data/raw/")
        return
    
    # Save to ONE consolidated JSON file
    extractor.save_to_consolidated_json(policies)
    
    # Generate and display summary
    summary = extractor.generate_summary_report(policies)
    
    print("\n" + "=" * 70)
    print("📊 EXTRACTION SUMMARY")
    print("=" * 70)
    print(f"   Total Policies: {summary['total_policies']}")
    print(f"   Countries: {len(summary['countries'])}")
    print(f"   Visa Types: {len(summary['visa_types'])}")
    print(f"   Total Characters: {summary['total_characters']:,}")
    print(f"   Average per Policy: {summary['average_characters_per_policy']:,} chars")
    
    print(f"\n📋 Countries:")
    for country, count in summary['countries'].items():
        print(f"   • {country}: {count} policies")
    
    print(f"\n📋 Visa Types:")
    for visa_type, count in summary['visa_types'].items():
        print(f"   • {visa_type}: {count} policies")
    
    print("\n" + "=" * 70)
    print(f"✅ EXTRACTION COMPLETE!")
    print(f"📁 ALL data in ONE file: {extractor.consolidated_output}")
    print("=" * 70)
    print("\n📋 Next Steps:")
    print(f"   1. Review consolidated file: {extractor.consolidated_output}")
    print("   2. Run: python chunk_policies.py")
    print("   3. Run: python create_vectorstore.py")
    print("=" * 70)


if __name__ == "__main__":
    main()