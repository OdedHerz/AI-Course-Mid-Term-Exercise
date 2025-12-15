"""
Insurance Claim PDF Generator - 10 Pages
Generates a comprehensive synthetic insurance claim document with timeline-based events.
Each page contains ~1200 characters for optimal hierarchical chunking.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import json
from datetime import datetime

def create_claim_content():
    """Generate the insurance claim content for 10 pages with metadata."""
    
    # Page 1: Introduction (~1200 chars with paragraph breaks every ~300 chars)
    intro_content = {
        "header": "Claim Introduction and Overview",
        "date": "2024-01-15",
        "involved_parties": ["Sarah Mitchell", "Progressive Auto Insurance", "Claims Department"],
        "type": "Overview",
        "text": """This insurance claim is filed under claim number CLM-2024-00789-AUTO and policy number PAI-8847562-2023. The claim was officially submitted on January 15, 2024, at 14:32:17 hours through Progressive Auto Insurance and will be processed according to standard company procedures.

The policyholder is Sarah Mitchell who holds a Comprehensive Auto Insurance policy covering the insured vehicle, a 2022 Honda Accord with vehicle identification number 1HGCV1F3XNA123456. The policy includes coverage of $500,000 for liability claims and $100,000 for collision damage to the insured vehicle.

A multi-vehicle collision occurred on January 15, 2024, at precisely 09:23:45 AM at the intersection of Maple Avenue and 5th Street in Downtown Seattle, Washington. The incident involved three vehicles total and resulted in significant property damage and minor personal injuries requiring immediate medical attention and subsequent police investigation.

Initial damage assessment conducted by certified insurance adjusters estimates the total claim value at $47,850 dollars including vehicle repairs and medical expenses. The incident occurred during morning rush hour traffic conditions with wet road surfaces from overnight rainfall. All involved parties have provided official statements to investigating officers."""
    }
    
    # Page 2: Initial Incident Event (~1200 chars with paragraph breaks every ~300 chars)
    event1_content = {
        "header": "Event 1: Initial Collision",
        "date": "2024-01-15 09:23:45",
        "involved_parties": ["Sarah Mitchell", "Robert Chen", "Seattle Police Department", "Officer James Wilson"],
        "type": "Details",
        "text": """The collision occurred on January 15, 2024, at exactly 09:23:45 AM at the intersection of Maple Avenue and 5th Street in Seattle, Washington, zip code 98101. GPS coordinates recorded at the scene were 47.6062 degrees North latitude and 122.3321 degrees West longitude for precise location documentation.

Policyholder Sarah Mitchell was traveling northbound on Maple Avenue at approximately 25 miles per hour in moderate traffic flow. Weather conditions at the time included light rain with temperature at 42 degrees Fahrenheit and visibility reduced to approximately 200 feet due to the precipitation. The traffic signal was displaying a green light for northbound traffic.

At precisely 09:23:45 hours, a 2019 Toyota Camry bearing license plate WA-ABC-1234 and driven by Robert Chen entered the intersection traveling eastbound on 5th Street at an estimated speed of 45 miles per hour. Security camera footage timestamped at 09:23:44 clearly shows Chen's vehicle entering the intersection against a red traffic signal.

The collision impact occurred on the driver's side front quarter panel of Mitchell's Honda Accord causing significant structural damage. Impact force caused Mitchell's vehicle to rotate counterclockwise and collide with a parked 2020 Ford F-150 bearing license plate WA-XYZ-7890. Vehicle airbags deployed in Mitchell's car at 09:23:46. Mitchell reported immediate neck pain and dizziness."""
    }
    
    # Page 3: Emergency Response Event (~1200 chars with paragraph breaks every ~300 chars)
    event2_content = {
        "header": "Event 2: Emergency Response and Assessment",
        "date": "2024-01-15 09:31:22",
        "involved_parties": ["Seattle Fire Department", "Medic Unit 47", "Paramedic Jennifer Ross", "Officer James Wilson", "Sarah Mitchell"],
        "type": "Details",
        "text": """First responders arrived at the collision scene at 09:31:22 AM on January 15, 2024. Response units included Seattle Fire Department Engine 10, Medic Unit 47, and Seattle Police Department Unit 3-Adam-12. Paramedic Jennifer Ross from Medic Unit 47 immediately assessed Mitchell's medical condition upon arrival at the scene.

Vital signs were recorded for Mitchell showing blood pressure of 145/92 millimeters of mercury and heart rate of 98 beats per minute. Mitchell was alert and oriented to person, place and time during the medical evaluation. She complained of significant neck stiffness and reported a headache with severity level of six out of ten on the standard pain scale.

Officer James Wilson from Seattle Police Department secured the intersection at 09:32:00 hours to preserve the accident scene. Photographic evidence was collected showing skid marks measuring exactly 47 feet from Chen's vehicle trajectory on the wet pavement. Traffic camera footage was retrieved showing signal timing that confirmed Chen entered the intersection 2.3 seconds after the light turned red.

Chen's vehicle maintenance records revealed that a brake system warning light had been active for 12 days prior to the incident. This critical finding was documented in the service center system under maintenance ticket number BRK-2024-0103. Property damage estimates totaled Mitchell vehicle $18,400, Chen vehicle $22,300, and parked F-150 $7,150."""
    }
    
    # Page 4: Investigation and Medical Follow-up (~1200 chars with paragraph breaks every ~300 chars)
    event3_content = {
        "header": "Event 3: Investigation and Medical Documentation",
        "date": "2024-01-15 14:45:18",
        "involved_parties": ["Dr. Michael Patterson", "Sarah Mitchell", "Claims Adjuster Linda Martinez", "Police Investigation Unit"],
        "type": "Details",
        "text": """Mitchell was transported to Seattle Medical Center Emergency Department by ambulance, arriving at 10:15:33 AM for medical evaluation. She was examined by Dr. Michael Patterson at 14:45:18 hours after initial triage and stabilization. The diagnosis included Grade 2 whiplash injury, cervical spine strain, and mild concussion from the impact.

A CT scan was performed at 15:23:00 which fortunately showed no structural damage to the cervical spine or brain tissue. The prescribed treatment plan includes physical therapy with 12 sessions recommended over six weeks, pain management medication consisting of Ibuprofen 600 milligrams three times daily, and use of a soft cervical collar for two weeks.

Claims Adjuster Linda Martinez conducted a comprehensive phone interview with Mitchell at 16:30:00 hours to document the incident details. Mitchell confirmed the complete timeline of events and provided dashboard camera footage clearly showing her vehicle traveling at 24 miles per hour at the moment of impact. Police report number SPD-2024-0156 was officially filed at 17:15:00.

The total estimated claim value is $47,850 dollars consisting of $44,010 for vehicle damage and $3,840 for medical expenses. Liability determination assigns 100 percent fault to Robert Chen based on traffic signal evidence, multiple witness statements, and official police citation. The claim was approved for processing at 18:22:33 with expected resolution of 15 to 20 business days."""
    }
    
    # Page 5: Vehicle Inspection & Repair Assessment (~1200 chars)
    event4_content = {
        "header": "Event 4: Vehicle Inspection and Repair Assessment",
        "date": "2024-01-16 10:30:00",
        "involved_parties": ["Premier Auto Body Shop", "Certified Inspector Thomas Blake", "Sarah Mitchell", "Progressive Insurance Adjuster"],
        "type": "Details",
        "text": """Mitchell's 2022 Honda Accord was transported to Premier Auto Body Shop on January 16, 2024, at 10:30:00 AM for comprehensive damage assessment. Certified Inspector Thomas Blake conducted a detailed examination using computerized diagnostic equipment and manual inspection protocols following industry standard procedures established by the National Institute for Automotive Service Excellence.

The inspection revealed extensive structural damage to the driver side A-pillar, B-pillar reinforcement bracket, and front subframe assembly requiring complete replacement. The left front suspension components including control arm, tie rod end, and wheel bearing assembly sustained impact damage. Total parts cost estimated at $12,450 with original equipment manufacturer components specified by the insurance policy coverage requirements.

Labor estimates calculated at 87.5 hours of certified technician work at the contracted rate of $95 per hour totaling $8,312.50 for the repair work. Additional costs include frame straightening equipment rental at $890, paint materials and color matching services at $2,340, and computerized wheel alignment calibration at $185. The complete repair timeline estimated at 14 to 18 business days.

Third-party vehicle appraiser David Richardson from Independent Auto Appraisers LLC reviewed the damage assessment on January 16 at 15:45:00 hours. Richardson verified all repair estimates and confirmed that the vehicle structural integrity can be fully restored. His independent appraisal report number IAA-2024-1567 supported the repair cost estimates provided by Premier Auto Body Shop."""
    }
    
    # Page 6: Medical Follow-up & Physical Therapy (~1200 chars)
    event5_content = {
        "header": "Event 5: Medical Follow-up and Physical Therapy",
        "date": "2024-01-22 08:00:00",
        "involved_parties": ["Dr. Michael Patterson", "Sarah Mitchell", "Physical Therapist Amanda Chen", "Seattle Rehabilitation Center"],
        "type": "Details",
        "text": """Mitchell attended her scheduled follow-up appointment with Dr. Michael Patterson at Seattle Medical Center on January 22, 2024, at 08:00:00 AM, exactly one week after the initial collision. The examination revealed continued cervical spine tenderness with restricted range of motion measured at 45 degrees rotation compared to normal 80 degrees. Pain level reported decreased from initial six out of ten to current four out of ten.

Dr. Patterson prescribed a comprehensive physical therapy program consisting of 12 sessions over six weeks at Seattle Rehabilitation Center. The treatment plan includes therapeutic exercises for cervical spine mobility, soft tissue massage therapy, electrical stimulation for pain management, and postural correction training. Mitchell was cleared to return to work with restrictions limiting heavy lifting to maximum 10 pounds.

Physical Therapist Amanda Chen conducted the initial therapy session on January 22 at 14:30:00 hours. The 60-minute session included baseline mobility assessment, gentle stretching exercises, heat therapy application for 15 minutes, and patient education on proper posture and home exercise routine. Mitchell tolerated the treatment well with no adverse reactions reported during or immediately after the session.

Progress notes documented in patient chart number PT-2024-0892 indicate good prognosis for full recovery within the six-week treatment window. Follow-up sessions scheduled for Mondays, Wednesdays, and Fridays at 14:30:00 hours. Total estimated medical treatment costs including physician follow-ups and physical therapy sessions calculated at $3,840 dollars, fully covered under Mitchell's comprehensive insurance policy benefits."""
    }
    
    # Page 7: Witness Statement Documentation (~1200 chars)
    event6_content = {
        "header": "Witness Statement and Traffic Analysis",
        "date": "2024-01-15 11:45:00",
        "involved_parties": ["Marcus Thompson", "Seattle Police Department", "Traffic Engineer Dr. Susan Miller", "Video Forensics Team"],
        "type": "Details",
        "text": """Witness Marcus Thompson provided a detailed sworn statement to Seattle Police Department at 11:45:00 AM on January 15, 2024. Thompson, who was waiting at the bus stop located at the southeast corner of the intersection, had an unobstructed view of the collision. His statement confirmed he observed Chen's vehicle approaching at high speed and entering the intersection against a red signal.

Thompson's testimony included specific observations: he noticed Chen's brake lights did not illuminate until after entering the intersection, the traffic signal had been red for approximately two seconds before Chen's vehicle entered, and he immediately called 911 at 09:24:33 providing his contact information and offering to remain at the scene as a witness. His statement was recorded as official witness testimony document number WT-2024-0156-001.

Traffic Engineer Dr. Susan Miller from Seattle Department of Transportation conducted a comprehensive analysis of the intersection traffic signal timing and road conditions. Her report documented that the traffic signal operates on a standard 90-second cycle with 35 seconds green phase for northbound traffic. Signal maintenance records confirmed the system was functioning correctly with the most recent inspection completed on January 10, 2024.

The Video Forensics Team analyzed footage from three different security cameras covering the intersection. Frame-by-frame analysis confirmed Chen's vehicle entered the intersection at timestamp 09:23:45.127 while the signal had transitioned to red at timestamp 09:23:42.850, providing definitive evidence supporting a 2.277 second red light violation. The forensic video analysis report was filed as evidence document VFA-2024-0156."""
    }
    
    # Page 8: Financial Breakdown & Policy Coverage (~1200 chars)
    event7_content = {
        "header": "Financial Breakdown and Insurance Coverage",
        "date": "2024-01-17 09:00:00",
        "involved_parties": ["Progressive Auto Insurance", "Claims Adjuster Linda Martinez", "Sarah Mitchell", "Finance Department"],
        "type": "Details",
        "text": """Progressive Auto Insurance Claims Adjuster Linda Martinez completed the comprehensive financial assessment on January 17, 2024, at 09:00:00 AM. The detailed breakdown itemizes all costs associated with the claim under file number CLM-2024-00789-AUTO. Mitchell's policy number PAI-8847562-2023 provides comprehensive coverage with a $500 deductible for collision claims and $100,000 maximum coverage limit per incident.

Vehicle damage costs totaling $44,010 include Premier Auto Body Shop repair estimate of $23,102.50, rental vehicle expenses for 18 days at $65 per day equaling $1,170, towing and storage fees of $485, diminished value assessment of $18,400, and administrative processing fees of $852.50. The rental vehicle authorization extends through the estimated repair completion date with daily rate pre-approved by the insurance carrier.

Medical expenses documented at $3,840 include emergency department treatment $1,250, CT scan and diagnostic imaging $890, physician consultation and follow-up appointments $625, physical therapy program 12 sessions at $95 per session totaling $1,140, prescription medications $185, and medical records processing fees $50. All medical costs pre-authorized and payable directly to healthcare providers under policy medical payments coverage.

Total claim value of $47,850 falls well within policy coverage limits. Mitchell's $500 deductible applies to the vehicle damage portion only, resulting in net payment to Mitchell of $43,510 for vehicle costs and $3,840 paid directly to medical providers. Claims processing timeline estimated at 15 to 20 business days with electronic funds transfer initiated upon claim approval and completion of all required documentation."""
    }
    
    # Page 9: Legal & Liability Documentation (~1200 chars)
    event8_content = {
        "header": "Legal Documentation and Liability Determination",
        "date": "2024-01-18 13:30:00",
        "involved_parties": ["Seattle Police Department", "Officer James Wilson", "Robert Chen", "Chen's Insurance - State Farm", "Legal Department"],
        "type": "Details",
        "text": """Seattle Police Department issued official traffic citation number TC-2024-0891 to Robert Chen on January 18, 2024, charging him with violation of Revised Code of Washington RCW 46.61.050 for failure to obey a traffic control device. The citation carries a mandatory court appearance requirement and fine of $500 plus court costs. Officer James Wilson documented the violation based on traffic camera evidence and witness testimony in official police report SPD-2024-0156.

Chen's insurance carrier State Farm Insurance was notified of the incident on January 15 at 16:45:00 hours. State Farm assigned claim number SF-2024-WA-12847 and Claims Representative Michael Torres to handle their insured's liability exposure. Torres contacted Progressive Insurance on January 17 to discuss subrogation and liability acceptance. Initial investigation by State Farm confirmed their insured's fault based on the comprehensive evidence package provided by Seattle Police Department.

State Farm issued formal liability acceptance letter on January 18, 2024, at 13:30:00 acknowledging 100 percent fault on behalf of their insured Robert Chen. The acceptance letter document number SF-LA-2024-12847 confirms their responsibility for all damages sustained by Sarah Mitchell including vehicle damage, medical expenses, lost wages, and any additional costs related to the collision incident. No dispute or litigation anticipated given clear liability evidence.

Progressive Auto Insurance Legal Department reviewed all documentation and confirmed the liability determination supports full claim approval. Legal counsel Patricia Anderson issued clearance memorandum LA-2024-0156 on January 18 at 15:00:00 authorizing claims payment processing. The subrogation recovery against State Farm Insurance initiated under file number SUB-2024-00789 to recover all costs paid to Mitchell including her deductible amount of $500 dollars."""
    }
    
    # Page 10: Claim Resolution Summary (type: Overview) (~1200 chars)
    event9_content = {
        "header": "Claim Resolution and Final Summary",
        "date": "2024-02-05",
        "involved_parties": ["Progressive Auto Insurance", "Sarah Mitchell", "Claims Department", "Finance Department"],
        "type": "Overview",
        "text": """Final claim resolution completed on February 5, 2024, for claim number CLM-2024-00789-AUTO under policy PAI-8847562-2023 for policyholder Sarah Mitchell. All documentation reviewed and approved by Progressive Auto Insurance Claims Department with authorization from Regional Claims Manager David Thompson. Total processing time from initial filing to final resolution was 21 calendar days meeting company service standards.

Total claim payout amount of $47,850 distributed as follows: vehicle damage settlement of $43,510 paid to Sarah Mitchell via electronic funds transfer on February 2, 2024, transaction reference number EFT-2024-02-00789. Medical expenses of $3,840 paid directly to healthcare providers Seattle Medical Center and Seattle Rehabilitation Center on February 3, 2024. Mitchell's $500 deductible to be recovered through subrogation from State Farm Insurance.

Vehicle repairs completed by Premier Auto Body Shop on January 30, 2024, with final inspection approval documented under quality control certificate QCC-2024-0156. Mitchell's vehicle returned to pre-accident condition with lifetime warranty on all structural repairs. Mitchell completed physical therapy program on February 1 with Dr. Patterson issuing full medical clearance with no permanent injury or ongoing treatment requirements anticipated.

Claim file officially closed on February 5, 2024, at 16:30:00 hours with final status code approved and settled. All parties satisfied with claim resolution. No appeals or disputes filed. Customer satisfaction survey completed by Mitchell rating service as excellent with five-star rating. Subrogation recovery in progress with estimated completion by March 15, 2024."""
    }
    
    return [intro_content, event1_content, event2_content, event3_content, event4_content, 
            event5_content, event6_content, event7_content, event8_content, event9_content]


def generate_pdf(filename="insurance_claim.pdf"):
    """Generate the PDF document with proper formatting."""
    
    # Create PDF document
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Container for the 'Flowable' objects
    story = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor='darkblue',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='darkblue',
        spaceAfter=12,
        spaceBefore=12
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        spaceAfter=6
    )
    
    # Get content
    pages_content = create_claim_content()
    
    # Build document
    for i, page_content in enumerate(pages_content):
        if i == 0:
            # Title page
            story.append(Paragraph("INSURANCE CLAIM DOCUMENT", title_style))
            story.append(Spacer(1, 0.2*inch))
        
        # Add header
        story.append(Paragraph(page_content["header"], header_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Add body text - split into paragraphs for better readability
        paragraphs = page_content["text"].split('\n\n')
        for para in paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), body_style))
                story.append(Spacer(1, 0.1*inch))
        
        # Add page break except for last page
        if i < len(pages_content) - 1:
            story.append(PageBreak())
    
    # Build PDF
    doc.build(story)
    print(f"[OK] PDF generated: {filename}")
    
    # Return content for metadata generation
    return pages_content


def generate_metadata(pages_content, filename="claim_metadata.json"):
    """Generate metadata JSON file."""
    
    metadata = {}
    
    for i, page_content in enumerate(pages_content, start=1):
        metadata[f"page_{i}"] = {
            "page_number": i,
            "header": page_content["header"],
            "involved_parties": page_content["involved_parties"],
            "date": page_content["date"],
            "type": page_content["type"],
            "character_count": len(page_content["text"])
        }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Metadata generated: {filename}")
    return metadata


def main():
    """Main execution function."""
    print("=" * 70)
    print("Insurance Claim PDF Generator - 10 Pages")
    print("=" * 70)
    print()
    
    # Generate PDF
    print("Generating 10-page PDF document...")
    pages_content = generate_pdf("insurance_claim.pdf")
    print()
    
    # Generate metadata
    print("Generating metadata...")
    metadata = generate_metadata(pages_content, "claim_metadata.json")
    print()
    
    # Display summary
    print("=" * 70)
    print("GENERATION SUMMARY")
    print("=" * 70)
    print(f"Total pages: {len(pages_content)}")
    print()
    print("Character counts per page:")
    for page_num, page_data in metadata.items():
        page_type = " (OVERVIEW)" if page_data['type'] == 'Overview' else ""
        print(f"  {page_num}: {page_data['character_count']} characters{page_type}")
    print()
    
    # Count Overview and Details pages
    overview_pages = [p for p in metadata.values() if p['type'] == 'Overview']
    details_pages = [p for p in metadata.values() if p['type'] == 'Details']
    print(f"Overview pages: {len(overview_pages)} (always included by Summary Agent)")
    print(f"Details pages: {len(details_pages)}")
    print()
    
    # Calculate chunking info
    chunk_size = 300
    overlap = 40
    print("Chunking Analysis:")
    print(f"  Chunk size: {chunk_size} characters")
    print(f"  Overlap: {overlap} characters")
    print()
    total_chunks = 0
    for page_num, page_data in metadata.items():
        chars = page_data['character_count']
        # Calculate approximate number of chunks
        # First chunk: 0-300, Second: 260-560, Third: 520-820, etc.
        effective_step = chunk_size - overlap
        num_chunks = ((chars - chunk_size) // effective_step) + 1 if chars >= chunk_size else 1
        total_chunks += num_chunks
        print(f"  {page_num}: ~{num_chunks} chunks")
    print()
    print(f"Total estimated chunks: ~{total_chunks}")
    print()
    
    print("[OK] All files generated successfully!")
    print()
    print("Output files:")
    print("  - insurance_claim.pdf (10 pages)")
    print("  - claim_metadata.json (10 pages)")
    print()
    print("Next steps:")
    print("  1. Review the generated PDF and metadata")
    print("  2. Run indexing to create chunks and summaries")
    print("  3. Test with query system")
    print("=" * 70)


if __name__ == "__main__":
    main()

