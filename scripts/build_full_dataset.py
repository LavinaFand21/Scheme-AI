import os
import json

# Define the full list of 48 government schemes with structured rules
full_schemes = [
    # 🌾 Agriculture & Farmers (8 schemes)
    {
        "id": "pm_kisan",
        "name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        "category": "Agriculture",
        "benefits": "Provides an income support of ₹6,000 per year in three equal installments of ₹2,000 directly into the bank accounts of eligible farmers.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 120,
            "max_income": 300000,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["Farmer"],
            "disability_required": False
        },
        "description": "PM-KISAN is a central sector scheme to provide financial assistance to landholding farmer families across India. The scheme aims to supplement the financial needs of farmers in procuring various inputs related to agriculture and allied activities.",
        "required_documents": [
            "Landholding Documents (Khasra Khatauni)",
            "Aadhaar Card",
            "Bank Account Details",
            "Mobile Number linked with Aadhaar"
        ],
        "application_steps": [
            "Go to the official PM-KISAN Portal (pmkisan.gov.in).",
            "Click on 'New Farmer Registration' on the Farmers Corner.",
            "Enter Aadhaar number and select state.",
            "Fill out the application form with personal details, land details, and bank account info.",
            "Upload land documents and submit."
        ],
        "official_portal": "https://pmkisan.gov.in"
    },
    {
        "id": "pmfby",
        "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "category": "Agriculture",
        "benefits": "Provides crop insurance cover against natural calamities, pests, and diseases. Farmers pay a low premium of 2% for Kharif and 1.5% for Rabi crops.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 120,
            "max_income": None,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["Farmer"],
            "disability_required": False
        },
        "description": "PMFBY is a crop insurance scheme launched to support sustainable production in agriculture sector by providing financial support to farmers suffering crop loss/damage arising out of unforeseen events.",
        "required_documents": [
            "Aadhaar Card",
            "Land Records (Khasra/Khatauni)",
            "Sowing Certificate from Patwari/Sarpanch",
            "Canceled Cheque or Bank Passbook copy"
        ],
        "application_steps": [
            "Visit the PMFBY Portal (pmfby.gov.in) or approach your nearest bank branch/CSC.",
            "Fill in the application form with crop details and land coordinates.",
            "Pay the nominal premium (1.5% to 2% depending on season).",
            "Submit the sowing certificate and land records.",
            "Receive the policy acknowledgment number."
        ],
        "official_portal": "https://pmfby.gov.in"
    },
    {
        "id": "kisan_credit_card",
        "name": "Kisan Credit Card (KCC)",
        "category": "Agriculture",
        "benefits": "Provides short-term credit and cash loans up to ₹3 Lakh at a very low interest rate of 4% per annum (after subvention).",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 75,
            "max_income": None,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["Farmer", "Labourer"],
            "disability_required": False
        },
        "description": "The KCC scheme aims to provide adequate and timely credit support from the banking system under a single window with flexible and simplified procedures for cultivation and other agricultural needs.",
        "required_documents": [
            "Aadhaar Card",
            "Land Ownership Documents",
            "Passport Size Photograph",
            "No-Dues Certificate from other local banks"
        ],
        "application_steps": [
            "Visit the official PM-KISAN portal or nearest commercial/rural bank.",
            "Download the KCC application form.",
            "Fill out personal, land, and crop cultivation details.",
            "Submit the form along with land records and ID proof.",
            "The bank verifies landholding and issues the KCC card."
        ],
        "official_portal": "https://pmkisan.gov.in"
    },
    {
        "id": "pmksy",
        "name": "PM Krishi Sinchayee Yojana (PMKSY) - Micro Irrigation",
        "category": "Agriculture",
        "benefits": "Provides up to 55% subsidy for small and marginal farmers (45% for other farmers) to set up micro-irrigation systems like drip and sprinkler irrigation.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 120,
            "max_income": None,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["Farmer"],
            "disability_required": False
        },
        "description": "PMKSY has been formulated with the vision of extending the coverage of irrigation ('Har Khet Ko Pani') and improving water use efficiency ('More Crop Per Drop') in a focused manner.",
        "required_documents": [
            "Aadhaar Card",
            "Land Map & Land Registry Copy",
            "Bank Passbook copy",
            "Water Source availability certificate"
        ],
        "application_steps": [
            "Visit your state's Agriculture Department website or local office.",
            "Apply online for the micro-irrigation subsidy.",
            "An agricultural officer will inspect the land and water source.",
            "Select an approved manufacturer/vendor to install drip/sprinkler components.",
            "The subsidy is released directly to the farmer/vendor account after verification."
        ],
        "official_portal": "https://pmksy.gov.in"
    },
    {
        "id": "soil_health_card",
        "name": "Soil Health Card Scheme",
        "category": "Agriculture",
        "benefits": "Provides free soil testing and a printed card containing nutrient status (12 parameters) and customized fertilizer recommendations to improve yield.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 120,
            "max_income": None,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["Farmer"],
            "disability_required": False
        },
        "description": "The scheme assists farmers in understanding the nutrient profile of their soil, helping them reduce fertilizer usage costs by applying exactly what the soil needs.",
        "required_documents": [
            "Aadhaar Card",
            "Land Identification Detail (Khasra Number)",
            "Mobile Number"
        ],
        "application_steps": [
            "Soil samples are collected from the farmer's field by local officers.",
            "Samples are analyzed in soil testing laboratories.",
            "A Soil Health Card is generated on the portal (soilhealth.dac.gov.in).",
            "The card is distributed to the farmer by local block officers or downloaded online."
        ],
        "official_portal": "https://soilhealth.dac.gov.in"
    },
    {
        "id": "enam",
        "name": "e-NAM (National Agriculture Market)",
        "category": "Agriculture",
        "benefits": "Access to a national online trading platform to sell agricultural produce directly to buyers across India, ensuring better prices and eliminating local middlemen.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 120,
            "max_income": None,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["Farmer"],
            "disability_required": False
        },
        "description": "e-NAM is a pan-India electronic trading portal which networks the existing APMC mandis to create a unified national market for agricultural commodities.",
        "required_documents": [
            "Aadhaar Card",
            "Bank Account details with IFSC",
            "Local Mandi Registration Certificate/Slip"
        ],
        "application_steps": [
            "Go to the e-NAM Portal (enam.gov.in) and register as a Farmer.",
            "Upload KYC documents and bank passbook image.",
            "Bring your harvested crop to an e-NAM integrated mandi.",
            "Get the produce weighed and quality tested at the lab.",
            "Sell online via auction and receive payments directly in your bank account."
        ],
        "official_portal": "https://enam.gov.in"
    },
    {
        "id": "pm_kisan_maandhan",
        "name": "PM Kisan Maandhan Yojana (PM-KMY)",
        "category": "Agriculture",
        "benefits": "Guarantees a monthly pension of ₹3,000 to small and marginal farmers after reaching the age of 60.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 40,
            "max_income": None,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["Farmer"],
            "disability_required": False
        },
        "description": "PM-KMY is a voluntary and contribution-based pension scheme for small and marginal farmers. Farmers contribute ₹55 to ₹200 per month (matched equally by the government) depending on their entry age.",
        "required_documents": [
            "Aadhaar Card",
            "Savings Bank Account Passbook",
            "Landholding Documents",
            "Consent form for auto-debit of subscription"
        ],
        "application_steps": [
            "Visit the nearest Common Service Centre (CSC) or maandhan.in.",
            "Provide Aadhaar and bank details for validation.",
            "The CSC operator calculates monthly contribution based on entry age.",
            "Complete auto-debit registration and sign the nomination form.",
            "Receive your unique Pension Account Number and card."
        ],
        "official_portal": "https://maandhan.in"
    },
    {
        "id": "pkvy",
        "name": "Paramparagat Krishi Vikas Yojana (PKVY)",
        "category": "Agriculture",
        "benefits": "Provides financial assistance of ₹50,000 per hectare over 3 years to support organic farming input procurement, harvesting, processing, and PGS certification.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 120,
            "max_income": None,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["Farmer"],
            "disability_required": False
        },
        "description": "PKVY promotes organic farming through a cluster approach. Groups of 50 or more farmers form organic farming clusters to get certified under PGS-India standards.",
        "required_documents": [
            "Aadhaar Card",
            "Land Ownership Documents",
            "Organic Cluster Registration/Group certificate"
        ],
        "application_steps": [
            "Form a group of at least 50 farmers representing a total cluster area of 50 acres.",
            "Register the organic cluster with the State Agriculture Department.",
            "Draft a PGS-India organic farming plan.",
            "Apply for organic inputs subsidy and organic certification on the PGS portal.",
            "Receive funds in the group's bank account."
        ],
        "official_portal": "https://dgap.gov.in"
    },

    # 🎓 Education & Scholarships (7 schemes)
    {
        "id": "nsp_pre_matric",
        "name": "National Scholarship Portal (NSP) - Pre-Matric Scholarship",
        "category": "Education",
        "benefits": "Provides ₹150 to ₹750 per month scholarship to students studying in Class 1 to 10 to help cover school expenses.",
        "eligibility_rules": {
            "min_age": 5,
            "max_age": 16,
            "max_income": 100000,
            "gender": "All",
            "states": ["All"],
            "caste": ["SC", "ST", "OBC"],
            "occupation": ["Student"],
            "disability_required": False
        },
        "description": "A scholarship scheme to encourage children from minority, SC, ST, and OBC families to study at the primary and secondary school levels and prevent dropouts.",
        "required_documents": [
            "Aadhaar Card of Student",
            "Caste Certificate",
            "Family Income Certificate (< 1 Lakh)",
            "Previous Year Marksheet/Class certificate",
            "Bank Account of Student or Parent"
        ],
        "application_steps": [
            "Go to the National Scholarship Portal (scholarships.gov.in).",
            "Register as a new student.",
            "Fill in personal, school, and bank details.",
            "Select 'Pre-Matric Scholarship' from the scheme list.",
            "Submit the application and download confirmation for school verification."
        ],
        "official_portal": "https://scholarships.gov.in"
    },
    {
        "id": "nsp_post_matric",
        "name": "National Scholarship Portal (NSP) - Post-Matric Scholarship",
        "category": "Education",
        "benefits": "Provides ₹3,000 to ₹20,000 per year scholarship (depending on technical/non-technical course) to support higher education tuition and maintenance fees.",
        "eligibility_rules": {
            "min_age": 15,
            "max_age": 30,
            "max_income": 250000,
            "gender": "All",
            "states": ["All"],
            "caste": ["SC", "ST", "OBC"],
            "occupation": ["Student"],
            "disability_required": False
        },
        "description": "Financial assistance for students from disadvantaged groups pursuing class 11, class 12, graduation, post-graduation, or professional diplomas/degrees.",
        "required_documents": [
            "Caste Certificate",
            "Family Income Certificate (< 2.5 Lakh)",
            "Marksheet of previous qualifying exam",
            "Admission fee receipt",
            "Bank Passbook copy"
        ],
        "application_steps": [
            "Register on the National Scholarship Portal (NSP).",
            "Complete student profile and upload course details.",
            "Apply under 'Post-Matric Scholarship Scheme' matching your caste/category.",
            "Upload scanned documents and submit.",
            "Verification is processed by your college and district nodal officer."
        ],
        "official_portal": "https://scholarships.gov.in"
    },
    {
        "id": "beti_bachao",
        "name": "Beti Bachao Beti Padhao - Sukanya Samriddhi Program",
        "category": "Education",
        "benefits": "Enables saving for a girl child's education and marriage with a high interest rate (currently 8.2%) and tax-free maturity under Sukanya Samriddhi.",
        "eligibility_rules": {
            "min_age": 0,
            "max_age": 10,
            "max_income": None,
            "gender": "Female",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["Student", "All"],
            "disability_required": False
        },
        "description": "BBBP aims to address the declining child sex ratio and promote girl child welfare, education, and financial security in India.",
        "required_documents": [
            "Birth Certificate of the Girl Child",
            "Aadhaar Card of Parent/Guardian",
            "PAN Card of Parent",
            "Initial deposit amount (Minimum ₹250)"
        ],
        "application_steps": [
            "Visit any post office or authorized commercial bank branch.",
            "Request the Sukanya Samriddhi Account (SSA) form.",
            "Fill in child and guardian details, attaching photographs.",
            "Submit birth certificate and KYC documents.",
            "Deposit the initial amount to activate the account."
        ],
        "official_portal": "https://www.indiapost.gov.in"
    },
    {
        "id": "sukanya_samriddhi",
        "name": "Sukanya Samriddhi Yojana (SSY)",
        "category": "Education",
        "benefits": "Offers high tax-free interest (8.2%) with maturity at age 21, designed to fund higher education and marriage expenses of girl children.",
        "eligibility_rules": {
            "min_age": 0,
            "max_age": 10,
            "max_income": None,
            "gender": "Female",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["Student", "All"],
            "disability_required": False
        },
        "description": "SSY is a small deposit scheme for girl children launched under the BBBP campaign. Parents can deposit from ₹250 to ₹1.5 Lakh per year for a maximum of 15 years.",
        "required_documents": [
            "Birth Certificate of the Girl Child",
            "Parent's Identity Proof (Aadhaar/PAN)",
            "Address Proof (Utility bill/Ration Card)"
        ],
        "application_steps": [
            "Approach an authorized bank or post office branch.",
            "Fill out the SSY account opening form.",
            "Submit child birth certificate and parent's identity proofs.",
            "Deposit the first annual contribution (minimum ₹250).",
            "Get the account passbook generated."
        ],
        "official_portal": "https://www.indiapost.gov.in"
    },
    {
        "id": "pm_vidya_lakshmi",
        "name": "PM Vidya Lakshmi Education Loan Scheme",
        "category": "Education",
        "benefits": "Provides collateral-free educational loans up to ₹6.5 Lakh with an interest subsidy for students from Economically Weaker Sections (EWS).",
        "eligibility_rules": {
            "min_age": 17,
            "max_age": 35,
            "max_income": None,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["Student"],
            "disability_required": False
        },
        "description": "Vidya Lakshmi is a first-of-its-kind portal for students seeking education loans. This portal has been developed under the guidance of the Department of Financial Services and Department of Higher Education.",
        "required_documents": [
            "Aadhaar Card & PAN Card",
            "College Admission Letter/Offer",
            "Detailed Fee Structure",
            "Academic Marksheets (Class 10, 12, etc.)",
            "Parent/Co-borrower Income Proof"
        ],
        "application_steps": [
            "Register on the Vidya Lakshmi Portal (vidyalakshmi.co.in).",
            "Fill out the Common Education Loan Application Form (CELAF).",
            "Select banks and branches where you wish to apply.",
            "Upload admission letter, fee structure, and KYC documents.",
            "Track status directly on the dashboard; the bank reviews and disburses funds."
        ],
        "official_portal": "https://www.vidyalakshmi.co.in"
    },
    {
        "id": "nmms",
        "name": "National Means-cum-Merit Scholarship (NMMS)",
        "category": "Education",
        "benefits": "Provides ₹12,000 per year (₹1,000 per month) scholarship from Class 9 to Class 12 to prevent talented students from dropping out after Class 8.",
        "eligibility_rules": {
            "min_age": 12,
            "max_age": 15,
            "max_income": 350000,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["Student"],
            "disability_required": False
        },
        "description": "A central scholarship for class 8 students studying in government or local body schools who clear the state-level NMMS exam and score at least 55% in class 7.",
        "required_documents": [
            "Class 7 Report Card with 55% marks",
            "Family Income Certificate (< 3.5 Lakh)",
            "Aadhaar Card of Student",
            "School Registration Certificate",
            "Caste Certificate (if applicable)"
        ],
        "application_steps": [
            "Apply for the NMMS selection test in Class 8 through your school principal.",
            "Appear for and clear the Mental Ability Test (MAT) and Scholastic Aptitude Test (SAT).",
            "Once selected, register on the National Scholarship Portal (NSP) in Class 9.",
            "Verify details and submit the application for scholarship disbursement."
        ],
        "official_portal": "https://scholarships.gov.in"
    },
    {
        "id": "pragati_scholarship",
        "name": "AICTE Pragati Scholarship for Girl Students",
        "category": "Education",
        "benefits": "Provides up to ₹50,000 per year towards tuition fees and purchase of books/equipment, plus a contingency allowance of ₹2,000 per month.",
        "eligibility_rules": {
            "min_age": 16,
            "max_age": 25,
            "max_income": 800000,
            "gender": "Female",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["Student"],
            "disability_required": False
        },
        "description": "AICTE scheme to support girls pursuing technical education (degree or diploma) at AICTE-approved colleges, limited to a maximum of 2 girls per family.",
        "required_documents": [
            "Aadhaar Card",
            "AICTE College Admission Letter & Fee receipt",
            "Family Income Certificate (< 8 Lakh)",
            "Class 10 and 12 Marksheets",
            "Declarations confirming single/max 2 girl children in family"
        ],
        "application_steps": [
            "Secure admission in a technical degree or diploma course at an AICTE approved college.",
            "Register on the National Scholarship Portal (NSP).",
            "Apply under 'AICTE Pragati Scholarship Scheme for Girl Students'.",
            "Upload KYC, fee details, and income documents.",
            "The institute verifies study records, and AICTE releases funds directly."
        ],
        "official_portal": "https://scholarships.gov.in"
    },

    # 🏠 Housing (3 schemes)
    {
        "id": "pmay_gramin",
        "name": "Pradhan Mantri Awas Yojana - Gramin (PMAY-G)",
        "category": "Housing",
        "benefits": "Provides direct financial assistance of ₹1.2 Lakh (plains) / ₹1.3 Lakh (hilly areas) for the construction of a permanent pucca house.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 120,
            "max_income": 300000,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["All"],
            "disability_required": False
        },
        "description": "PMAY-G aims to provide a pucca house with basic amenities to all homeless householders and those households living in dilapidated houses in rural areas.",
        "required_documents": [
            "Aadhaar Card",
            "Ration Card or BPL Identity Proof",
            "Bank Passbook copy",
            "SECC 2011 Job card or registration details"
        ],
        "application_steps": [
            "Beneficiaries are identified automatically based on SECC 2011 housing deprivation data.",
            "The list is verified by the local Gram Sabha.",
            "Apply online through the PMAY-G portal or Gram Panchayat office.",
            "An inspector visits the current kutcha house and takes geo-tagged photos.",
            "Funds are disbursed in installments directly to your bank account as construction progresses."
        ],
        "official_portal": "https://pmayg.nic.in"
    },
    {
        "id": "pmay_urban",
        "name": "Pradhan Mantri Awas Yojana - Urban (PMAY-U)",
        "category": "Housing",
        "benefits": "Provides an interest subsidy of 3% to 6.5% on home loans, offering up to ₹2.67 Lakh subsidy for EWS, LIG, and MIG categories buying their first house.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 70,
            "max_income": 1800000,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["All"],
            "disability_required": False
        },
        "description": "PMAY-U targets the housing requirements of the urban poor, including slum dwellers, EWS, LIG, and Middle Income Groups (MIG) in cities.",
        "required_documents": [
            "Aadhaar Card & PAN Card",
            "Annual Income Certificate / Salary slips / Form 16",
            "Affidavit stating no pucca house is owned in India",
            "Property ownership documents/purchase agreements"
        ],
        "application_steps": [
            "Log in to the official PMAY portal (pmaymis.gov.in).",
            "Select 'Citizen Assessment' and choose the category (Credit Linked Subsidy Scheme).",
            "Fill in personal, bank, and income details.",
            "Apply for a home loan through any commercial bank, selecting PMAY subsidy.",
            "The bank processes the loan and claims the interest subsidy from the government."
        ],
        "official_portal": "https://pmaymis.gov.in"
    },
    {
        "id": "rajiv_gandhi_awas",
        "name": "Rajiv Awas Yojana (Slum Rehabilitation PMAY Extension)",
        "category": "Housing",
        "benefits": "Provides free or highly subsidized permanent housing and basic civic infrastructure (water, sanitation, electricity) for registered slum dwellers.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 120,
            "max_income": 150000,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["Labourer", "Other"],
            "disability_required": False
        },
        "description": "Designed to create a slum-free India, this scheme focuses on in-situ slum rehabilitation by constructing permanent flats/multi-story housing on municipal land for slum dwellers.",
        "required_documents": [
            "Slum Dweller Identity Card / Survey slip",
            "Aadhaar Card",
            "Proof of residence in slum before cutoff date",
            "Income Certificate"
        ],
        "application_steps": [
            "The municipal corporation conducts a detailed household survey in notified slums.",
            "Slum dwellers register and submit identity/residence proof.",
            "A rehabilitation block plan is approved.",
            "Temporary transit housing is provided during construction.",
            "Permanent flats are allotted through a lucky draw once construction is finished."
        ],
        "official_portal": "https://mohua.gov.in"
    },

    # 🏥 Health & Insurance (6 schemes)
    {
        "id": "ayushman_bharat",
        "name": "Ayushman Bharat Pradhan Mantri Jan Arogya Yojana (PM-JAY)",
        "category": "Health",
        "benefits": "Provides free health insurance cover of up to ₹5 Lakh per family per year for secondary and tertiary care hospitalization across public and private hospitals.",
        "eligibility_rules": {
            "min_age": 0,
            "max_age": 120,
            "max_income": 150000,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["All"],
            "disability_required": False
        },
        "description": "Ayushman Bharat PM-JAY is the largest health assurance scheme in the world, targeting poor and vulnerable families based on SECC 2011 demographic indicators.",
        "required_documents": [
            "Aadhaar Card or Ration Card",
            "Family Identity Proof",
            "Income Certificate",
            "Active Mobile Number"
        ],
        "application_steps": [
            "Visit the nearest Common Service Centre (CSC) or empanelled hospital.",
            "Check eligibility on the 'Am I Eligible' portal using mobile number/ration card.",
            "Get family identity verified by Ayushman Mitra.",
            "Collect the Ayushman Golden Card for cashless hospital treatments."
        ],
        "official_portal": "https://pmjay.gov.in"
    },
    {
        "id": "pmsby",
        "name": "Pradhan Mantri Suraksha Bima Yojana (PMSBY)",
        "category": "Health",
        "benefits": "Provides accidental death and full disability insurance cover of ₹2 Lakh (₹1 Lakh for partial disability) for a premium of just ₹20 per year.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 70,
            "max_income": None,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["All"],
            "disability_required": False
        },
        "description": "An accidental death and disability cover insurance scheme administered through public sector general insurance companies, auto-debited annually from the subscriber's bank account.",
        "required_documents": [
            "Savings Bank Account Passbook",
            "Aadhaar Card",
            "Nominee Details"
        ],
        "application_steps": [
            "Approach the bank branch holding your savings account.",
            "Request the PMSBY registration form.",
            "Fill in Aadhaar, mobile number, and nominee details.",
            "Check the box for auto-debit consent.",
            "Confirm registration via SMS if using net banking/mobile banking."
        ],
        "official_portal": "https://jansuraksha.gov.in"
    },
    {
        "id": "pmjjby",
        "name": "Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY)",
        "category": "Health",
        "benefits": "Provides a life insurance cover of ₹2 Lakh for death due to any cause, for a low premium of ₹436 per year.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 50,
            "max_income": None,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["All"],
            "disability_required": False
        },
        "description": "PMJJBY is a government-backed life insurance scheme, auto-renewed every year on May 31st via auto-debit from the subscriber's linked bank account.",
        "required_documents": [
            "Savings Bank Account Passbook",
            "Aadhaar Card",
            "Nominee Details"
        ],
        "application_steps": [
            "Approach the bank branch where you hold a savings account.",
            "Fill out the PMJJBY Enrollment Form.",
            "Provide Aadhaar and nominee details, signing the auto-debit authorization.",
            "Ensure the annual premium (₹436) is in the account by May 25th each year."
        ],
        "official_portal": "https://jansuraksha.gov.in"
    },
    {
        "id": "janani_suraksha",
        "name": "Janani Suraksha Yojana (JSY)",
        "category": "Health",
        "benefits": "Provides a cash incentive of ₹1,400 (rural) / ₹1,000 (urban) to pregnant women from BPL families for giving birth in government hospitals.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 45,
            "max_income": 120000,
            "gender": "Female",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["All"],
            "disability_required": False
        },
        "description": "JSY is a safe motherhood intervention under the National Health Mission. It aims to reduce maternal and neonatal mortality by promoting institutional deliveries among low-income pregnant women.",
        "required_documents": [
            "JSY Card / ANC Registration card",
            "Aadhaar Card",
            "BPL Ration Card or Income Certificate",
            "Bank Account copy"
        ],
        "application_steps": [
            "Register your pregnancy at the local government health sub-centre or primary health centre.",
            "Get a Mother and Child Protection (MCP) card.",
            "Coordinate with local ASHA worker for institutional delivery.",
            "Get admitted to a government hospital for delivery.",
            "The ASHA worker processes JSY benefits directly into the mother's account post-delivery."
        ],
        "official_portal": "https://nhm.gov.in"
    },
    {
        "id": "pm_matru_vandana",
        "name": "Pradhan Mantri Matru Vandana Yojana (PMMVY)",
        "category": "Health",
        "benefits": "Provides direct cash incentives of ₹5,000 in three installments to pregnant women and lactating mothers for nutrition and wage loss compensation.",
        "eligibility_rules": {
            "min_age": 19,
            "max_age": 45,
            "max_income": 800000,
            "gender": "Female",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["All"],
            "disability_required": False
        },
        "description": "PMMVY supports pregnant women for their first live birth. The cash transfers encourage adequate rest, health checkups, and early immunization cycles.",
        "required_documents": [
            "Mother and Child Protection (MCP) Card",
            "Identity Proof (Aadhaar Card)",
            "Husband's Aadhaar Card",
            "Bank Account Passbook",
            "Pregnancy Registration Certificate"
        ],
        "application_steps": [
            "Register at an Anganwadi Centre (AWC) or health facility within 150 days of LMP.",
            "Submit Form 1A along with Aadhaar, bank passbook, and MCP card details.",
            "Submit Form 1B after completing at least one antenatal checkup for the 2nd installment.",
            "Submit Form 1C after child birth registration and initial vaccination cycle for the 3rd installment."
        ],
        "official_portal": "https://pmmvy-cas.nic.in"
    },
    {
        "id": "rsby",
        "name": "Rashtriya Swasthya Bima Yojana (RSBY)",
        "category": "Health",
        "benefits": "Provides cashless hospitalization coverage of up to ₹30,000 per year for a family of 5, for registered unorganized sector workers.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 60,
            "max_income": 150000,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["Labourer", "Other"],
            "disability_required": False
        },
        "description": "RSBY is a government-run health insurance scheme for BPL families and unorganized sector workers, utilizing smart cards to provide biometric validation and cashless treatment.",
        "required_documents": [
            "Ration Card / BPL card",
            "Aadhaar Card",
            "RSBY Smart Card (issued on spot during registration)",
            "Registration fee (₹30)"
        ],
        "application_steps": [
            "The district administration publishes a list of BPL families.",
            "A mobile registration team visits the village/locality.",
            "Bring BPL card and register using fingerprint biometrics.",
            "Pay the ₹30 registration fee.",
            "Get the printed RSBY Smart card immediately with your photo."
        ],
        "official_portal": "http://www.rsby.gov.in"
    },

    # 💼 Employment & Skill (5 schemes)
    {
        "id": "pmkvy",
        "name": "PM Kaushal Vikas Yojana (PMKVY)",
        "category": "Employment & Skill",
        "benefits": "Provides free industry-relevant skill training, standard certification, financial reward of up to ₹8,000, and job placement support.",
        "eligibility_rules": {
            "min_age": 15,
            "max_age": 45,
            "max_income": None,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["Student", "Other"],
            "disability_required": False
        },
        "description": "PMKVY is the flagship outcome-based skill training scheme of the Ministry of Skill Development & Entrepreneurship (MSDE) aimed at enabling youth to take up industry-relevant skill training.",
        "required_documents": [
            "Aadhaar Card",
            "Educational Qualification Certificates",
            "Bank Passbook copy",
            "Passport Size Photograph"
        ],
        "application_steps": [
            "Go to the Skill India Digital Portal (skillindiadigital.gov.in).",
            "Search for a local PMKVY training partner and course.",
            "Register for a batch online or visit the training centre directly.",
            "Attend the training sessions and complete assessment tests.",
            "Receive your Skill Certificate and direct financial reward upon success."
        ],
        "official_portal": "https://www.skillindiadigital.gov.in"
    },
    {
        "id": "mgnregs",
        "name": "Mahatma Gandhi National Rural Employment Guarantee Scheme (MGNREGS)",
        "category": "Employment & Skill",
        "benefits": "Guarantees 100 days of manual unskilled wage employment per financial year to every rural household, paying ₹220 to ₹350 per day depending on state.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 120,
            "max_income": None,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["Labourer", "Farmer"],
            "disability_required": False
        },
        "description": "MGNREGS is a labor law and social security measure that aims to guarantee the 'right to work' by enhancing livelihood security in rural areas of India.",
        "required_documents": [
            "Aadhaar Card",
            "Ration Card",
            "Bank Account details",
            "Photograph for Job Card"
        ],
        "application_steps": [
            "Apply for a Job Card at the local Gram Panchayat office.",
            "Submit family details and passport photo.",
            "Receive the Job Card within 15 days.",
            "Submit a written application requesting work (Gram Panchayat will assign work within 5km radius).",
            "Complete work and receive wages directly in your bank account weekly."
        ],
        "official_portal": "https://nrega.nic.in"
    },
    {
        "id": "eshram",
        "name": "e-Shram Card Portal Registration",
        "category": "Labour & Employment",
        "benefits": "Provides a unique Universal Account Number (UAN) card, ₹2 Lakh accidental death/disability insurance cover, and direct access to various central and state social welfare schemes.",
        "eligibility_rules": {
            "min_age": 16,
            "max_age": 59,
            "max_income": 300000,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["Labourer", "Farmer"],
            "disability_required": False
        },
        "description": "e-Shram is a comprehensive national database of unorganized workers (migrant workers, street vendors, domestic help, agricultural workers) to deliver targeted government benefits.",
        "required_documents": [
            "Aadhaar Card",
            "Mobile number linked with Aadhaar",
            "Bank Account Number with IFSC"
        ],
        "application_steps": [
            "Open the e-Shram Portal (eshram.gov.in).",
            "Click on 'Register on e-Shram'.",
            "Enter Aadhaar-linked mobile number and captcha, then enter OTP.",
            "Fill in personal, residential, educational, occupational, and bank account details.",
            "Verify details, submit, and download the UAN (Universal Account Number) e-Shram Card."
        ],
        "official_portal": "https://eshram.gov.in"
    },
    {
        "id": "startup_india",
        "name": "Startup India Initiative",
        "category": "Employment & Skill",
        "benefits": "Provides tax exemption for 3 consecutive years, fast-track patent processing, self-certification under labor laws, and access to a ₹10,000 Crore fund of funds.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 120,
            "max_income": None,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["Entrepreneur"],
            "disability_required": False
        },
        "description": "Startup India aims to build a strong ecosystem for nurturing innovation and startups, generating employment, and driving sustainable economic growth.",
        "required_documents": [
            "Incorporation or Registration Certificate of Business",
            "PAN Card of the Entity",
            "Brief Write-up/Pitch explaining the innovative nature of business",
            "Patent/Trademark registrations (if any)"
        ],
        "application_steps": [
            "Incorporate your business as a Private Limited Company, Partnership, or LLP.",
            "Go to startupindia.gov.in and register your profile.",
            "Apply for DPIIT Recognition by uploading incorporation certificates and pitch details.",
            "Once recognized, apply for tax exemption under Section 56 and Section 80-IAC.",
            "Avail benefits of fast-track patents and government tenders."
        ],
        "official_portal": "https://www.startupindia.gov.in"
    },
    {
        "id": "pm_svanidhi",
        "name": "PM SVANidhi (Street Vendor Loan Scheme)",
        "category": "Employment & Skill",
        "benefits": "Offers collateral-free working capital microloans of ₹10,000 (1st tranche) → ₹20,000 (2nd tranche) → ₹50,000 (3rd tranche) with a 7% interest subsidy.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 70,
            "max_income": None,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["Entrepreneur", "Labourer"],
            "disability_required": False
        },
        "description": "PM SVANidhi supports street vendors, hawkers, and cart sellers in urban, peri-urban, and rural areas who lost their livelihoods due to COVID-19 lockdowns.",
        "required_documents": [
            "Aadhaar Card",
            "Voter ID / Driving License",
            "Certificate of Vending (CoV) or Letter of Recommendation from local body",
            "Bank Account details"
        ],
        "application_steps": [
            "Visit the PM SVANidhi Portal (pmsvanidhi.mohua.gov.in) or download the app.",
            "Enter your Aadhaar-linked mobile number to check eligibility.",
            "Upload your Letter of Recommendation (LoR) or Vending Certificate.",
            "Select a lending institution (commercial bank, rural bank, or microfinance).",
            "The loan is processed and disbursed directly to your bank account."
        ],
        "official_portal": "https://pmsvanidhi.mohua.gov.in"
    },

    # 👩 Women Empowerment (5 schemes)
    {
        "id": "mudra_women",
        "name": "Pradhan Mantri Mudra Yojana (PMMY) - Women Entrepreneurs",
        "category": "Women Empowerment",
        "benefits": "Provides collateral-free loans up to ₹10 Lakh (Shishu, Kishor, Tarun tranches) with low interest rates and flexible repayment options for women-owned micro/small businesses.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 65,
            "max_income": None,
            "gender": "Female",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["Entrepreneur"],
            "disability_required": False
        },
        "description": "PMMY encourages financial independence among women by providing simplified, zero-collateral credit lines for setting up or expanding business ventures in non-farm sectors.",
        "required_documents": [
            "Mudra Application Form",
            "Business Plan / Project Report",
            "Identity Proof (Aadhaar/PAN)",
            "Address Proof of Residence & Business",
            "Quotations for machinery/raw materials to be purchased"
        ],
        "application_steps": [
            "Prepare a business project plan.",
            "Approach a bank, microfinance institution, or apply online at udyamimitra.in.",
            "Submit the Mudra loan application form under the appropriate category (Shishu up to 50k, Kishor up to 5L, Tarun up to 10L).",
            "Submit personal identity, business address, and project proofs.",
            "The bank reviews, sanctions, and disburses the credit."
        ],
        "official_portal": "https://www.mudra.org.in"
    },
    {
        "id": "standup_india",
        "name": "Stand-Up India Scheme for Women",
        "category": "Women Empowerment",
        "benefits": "Provides bank loans between ₹10 Lakh and ₹1 Crore for setting up a greenfield (new) enterprise in manufacturing, services, agri-allied, or trading.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 70,
            "max_income": None,
            "gender": "Female",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["Entrepreneur"],
            "disability_required": False
        },
        "description": "Stand-Up India promotes entrepreneurship among women and SC/ST communities by ensuring that at least one woman or SC/ST borrower per commercial bank branch receives a business loan.",
        "required_documents": [
            "Aadhaar Card",
            "Business Plan / Project Report",
            "Proof of Greenfield Enterprise status",
            "Company incorporation or partnership papers",
            "Last 3 years audited balance sheets (if applicable)"
        ],
        "application_steps": [
            "Go to the Stand-Up India Portal (standupmitra.in).",
            "Register as a prospective borrower.",
            "Fill in business details and choose whether handholding support is needed.",
            "Submit the online application. The portal connects you to banks.",
            "The bank performs checks and disburses the credit."
        ],
        "official_portal": "https://www.standupmitra.in"
    },
    {
        "id": "mahila_shakti_kendra",
        "name": "Mahila Shakti Kendra (MSK)",
        "category": "Women Empowerment",
        "benefits": "Provides rural women with access to skill training, digital literacy, health awareness, employment support, and legal rights knowledge through village level hubs.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 120,
            "max_income": None,
            "gender": "Female",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["All"],
            "disability_required": False
        },
        "description": "MSK is a centrally sponsored scheme under the Ministry of Women and Child Development to empower rural women through community participation and digital interface hubs.",
        "required_documents": [
            "Aadhaar Card",
            "Resident Certificate",
            "Mobile Number"
        ],
        "application_steps": [
            "Visit the nearest Mahila Shakti Kendra, Anganwadi Centre, or Block Development Office.",
            "Submit your profile and identify areas where you need support (e.g. digital training, skill courses).",
            "Enroll in the upcoming local training sessions or awareness camps.",
            "Participate in the certificate courses."
        ],
        "official_portal": "https://wcd.nic.in"
    },
    {
        "id": "free_sewing_machine",
        "name": "Free Sewing Machine Scheme (PMEGP Extension)",
        "category": "Women Empowerment",
        "benefits": "Provides a free sewing machine worth ₹15,000 to ₹20,000 to encourage self-employment among women, prioritizing widows and disabled women.",
        "eligibility_rules": {
            "min_age": 20,
            "max_age": 40,
            "max_income": 12000,
            "gender": "Female",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["Labourer", "Other"],
            "disability_required": False
        },
        "description": "An initiative to empower women in rural and urban areas by providing them with free sewing machines, enabling them to start home tailoring businesses.",
        "required_documents": [
            "Aadhaar Card & Birth Certificate",
            "Income Certificate showing family income < ₹12,000/year",
            "Widow Certificate or Disability Certificate (if applicable)",
            "Passport Size Photograph"
        ],
        "application_steps": [
            "Go to the local District Industry Centre (DIC) or state government portal.",
            "Download the Free Sewing Machine Scheme application form.",
            "Fill in personal, income, and bank account details.",
            "Attach income certificate, Aadhaar, and photo.",
            "Submit the physical form to the DIC office. Eligible candidates receive the sewing machine or direct bank transfer."
        ],
        "official_portal": "https://pmegp.gov.in"
    },
    {
        "id": "ujjwala",
        "name": "Pradhan Mantri Ujjwala Yojana (PMUY)",
        "category": "Women Empowerment",
        "benefits": "Provides a free, deposit-free LPG connection, a stove, and the first gas cylinder refill completely free to BPL households.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 120,
            "max_income": None,
            "gender": "Female",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["All"],
            "disability_required": False
        },
        "description": "PMUY aims to safeguard the health of women and children by providing clean cooking fuel (LPG) instead of hazardous firewood or coal.",
        "required_documents": [
            "BPL Ration Card or SECC 2011 listing",
            "Aadhaar Card of the female applicant",
            "Bank Passbook copy",
            "Address Proof (Utility bill/Ration Card)"
        ],
        "application_steps": [
            "Visit the nearest LPG distributor (Indane, HP, Bharat Gas).",
            "Request the Ujjwala connection application form.",
            "Fill in details and attach Aadhaar, BPL card, and bank passbook.",
            "The distributor verifies the address and validates details on the national portal.",
            "Collect the LPG cylinder, regulator, and stove."
        ],
        "official_portal": "https://www.pmuy.gov.in"
    },

    # 👴 Senior Citizens & Pension (4 schemes)
    {
        "id": "pm_vaya_vandana",
        "name": "PM Vaya Vandana Yojana (PMVVY)",
        "category": "Senior Citizens",
        "benefits": "Offers an assured pension return of 7.4% per annum for 10 years, with monthly, quarterly, or annual payout options. Max investment is ₹15 Lakh.",
        "eligibility_rules": {
            "min_age": 60,
            "max_age": 120,
            "max_income": None,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["All"],
            "disability_required": False
        },
        "description": "PMVVY is a pension scheme for senior citizens administered through the Life Insurance Corporation (LIC) of India. It provides social security during old age.",
        "required_documents": [
            "Aadhaar Card",
            "Age Proof Document (PAN/Birth Certificate)",
            "Bank Account details for pension payouts",
            "Passport Size Photograph"
        ],
        "application_steps": [
            "Visit the LIC portal (licindia.in) or any LIC branch.",
            "Request the PMVVY application form.",
            "Choose your payout frequency (monthly/quarterly/yearly) and purchase price.",
            "Submit KYC and bank details.",
            "Pay the lump-sum investment amount to activate the pension plan."
        ],
        "official_portal": "https://licindia.in"
    },
    {
        "id": "atal_pension",
        "name": "Atal Pension Yojana (APY)",
        "category": "Senior Citizens",
        "benefits": "Guarantees a monthly pension ranging from ₹1,000 to ₹5,000 after reaching age 60, based on subscription contributions.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 40,
            "max_income": None,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["All"],
            "disability_required": False
        },
        "description": "APY is a pension scheme focused on unorganized sector workers to provide financial security in old age. Administered by PFRDA.",
        "required_documents": [
            "Savings Bank Account Passbook",
            "Aadhaar Card",
            "Mobile Number",
            "Nominee Details"
        ],
        "application_steps": [
            "Approach the bank branch where you hold a savings account.",
            "Fill out the APY Registration Form.",
            "Provide Aadhaar and mobile number, and set up auto-debit option.",
            "Ensure sufficient balance in bank account for periodic contributions."
        ],
        "official_portal": "https://www.npscra.nsdl.co.in"
    },
    {
        "id": "ignops",
        "name": "Indira Gandhi National Old Age Pension Scheme (IGNOAPS)",
        "category": "Senior Citizens",
        "benefits": "Provides a monthly pension of ₹200 (for ages 60-79) and ₹500 (for age 80+) to senior citizens from BPL families.",
        "eligibility_rules": {
            "min_age": 60,
            "max_age": 120,
            "max_income": 120000,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["All"],
            "disability_required": False
        },
        "description": "IGNOAPS is a centrally sponsored non-contributory old age pension scheme implemented under the National Social Assistance Programme (NSAP).",
        "required_documents": [
            "Aadhaar Card",
            "Age Proof Document",
            "BPL Ration Card",
            "Bank Account Passbook"
        ],
        "application_steps": [
            "Approach the local Gram Panchayat office (rural) or Municipal Office (urban).",
            "Request the NSAP Pension Form.",
            "Fill in details and attach BPL card copy and age proof.",
            "Submit to the block development officer or municipal commissioner.",
            "Once approved, the pension is credited directly to your bank account monthly."
        ],
        "official_portal": "https://nsap.nic.in"
    },
    {
        "id": "scss",
        "name": "Senior Citizen Savings Scheme (SCSS)",
        "category": "Senior Citizens",
        "benefits": "Offers a high interest rate of 8.2% per annum with quarterly payouts, for a maximum deposit of up to ₹30 Lakh, plus tax benefits under 80C.",
        "eligibility_rules": {
            "min_age": 60,
            "max_age": 120,
            "max_income": None,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["All"],
            "disability_required": False
        },
        "description": "SCSS is a government-backed retirement benefits program for seniors aged 60 and above (or 55+ for those retiring early under VRS).",
        "required_documents": [
            "Aadhaar Card & PAN Card",
            "Age Proof Document",
            "Retirement documents / VRS certificate (if applying under age 60)",
            "Cheque/Cash for deposit"
        ],
        "application_steps": [
            "Visit any post office or authorized commercial bank branch.",
            "Fill out the SCSS account opening form.",
            "Submit KYC details and retirement proofs.",
            "Deposit the investment amount (minimum ₹1,000, maximum ₹30 Lakh).",
            "The account is activated, and interest is paid quarterly."
        ],
        "official_portal": "https://www.indiapost.gov.in"
    },

    # 🔨 Labour & Unorganized Workers (4 schemes)
    {
        "id": "bocw",
        "name": "BOCW Welfare Board Registration (Construction Workers)",
        "category": "Labour",
        "benefits": "Provides registered construction workers with accident insurance, educational grants for children, tool-kit allowances, maternity benefits, and pension.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 60,
            "max_income": None,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["Labourer"],
            "disability_required": False
        },
        "description": "The Building and Other Construction Workers (BOCW) Welfare Board protects the interests of workers engaged in construction, masonry, stone-cutting, and painting activities.",
        "required_documents": [
            "Aadhaar Card",
            "90-Day Work Certificate from contractor or local union",
            "Bank Passbook copy",
            "Passport Size Photograph"
        ],
        "application_steps": [
            "Go to your state's Labour Department or BOCW portal (e.g. upbocw.in, bocw.delhi.gov.in).",
            "Register as a Construction Worker.",
            "Upload 90-day work certificate and bank passbook.",
            "Pay the nominal registration fee (usually ₹20-50).",
            "The block officer verifies documents and issues the BOCW card."
        ],
        "official_portal": "https://shramsuvidha.gov.in"
    },
    {
        "id": "esic",
        "name": "Employee State Insurance Corporation (ESIC)",
        "category": "Labour",
        "benefits": "Provides full medical care for self and family, sickness cash benefits (70% of wages), maternity benefits, and permanent disability pension.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 60,
            "max_income": 252000,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["Labourer", "Other"],
            "disability_required": False
        },
        "description": "ESIC is an integrated multidimensional social security system providing socio-economic protection to workers in organized sector earning up to ₹21,000 per month.",
        "required_documents": [
            "Aadhaar Card",
            "Employer Registration copy",
            "Salary slip / Bank account proof"
        ],
        "application_steps": [
            "The employer registers the employee on the ESIC portal (esic.gov.in).",
            "The employee fills in nominee and family details.",
            "The employer generates the ESIC Pehchan identity card.",
            "The employee visits the local ESI dispensary to complete biometric photo registration.",
            "Avail cashless medical treatments at any ESI hospital."
        ],
        "official_portal": "https://www.esic.gov.in"
    },
    {
        "id": "epfo",
        "name": "Employees' Provident Fund Organization (EPFO)",
        "category": "Labour",
        "benefits": "Mandatory savings fund (12% employee + 12% employer contribution), monthly pension (EPS) after retirement, and ₹7 Lakh life insurance (EDLI).",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 60,
            "max_income": 180000,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["Labourer", "Other"],
            "disability_required": False
        },
        "description": "EPFO administers a compulsory provident fund, pension, and insurance program for salaried employees in establishments employing 20 or more persons.",
        "required_documents": [
            "Aadhaar Card & PAN Card",
            "Universal Account Number (UAN)",
            "Bank Account details"
        ],
        "application_steps": [
            "The employer registers the establishment on the EPFO member portal.",
            "The employer registers the employee and generates a unique 12-digit UAN.",
            "The employee logs in to the Member e-Sewa portal and completes UAN activation.",
            "Link Aadhaar, PAN, and bank details (KYC) to the portal.",
            "Track monthly PF contributions and make online withdrawals when needed."
        ],
        "official_portal": "https://www.epfindia.gov.in"
    },
    {
        "id": "pm_sym",
        "name": "Pradhan Mantri Shram Yogi Maandhan (PM-SYM)",
        "category": "Labour",
        "benefits": "Guarantees a monthly pension of ₹3,000 to unorganized sector workers after reaching age 60.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 40,
            "max_income": 180000,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["Labourer"],
            "disability_required": False
        },
        "description": "PM-SYM is a pension scheme for unorganized workers (street vendors, agricultural workers, construction workers) earning less than ₹15,000/month, who are not members of EPFO/ESIC.",
        "required_documents": [
            "Aadhaar Card",
            "Savings Bank Account Passbook",
            "Mobile Number"
        ],
        "application_steps": [
            "Visit the nearest Common Service Centre (CSC) or maandhan.in.",
            "Provide Aadhaar and bank details for verification.",
            "Set up the auto-debit consent for monthly contributions (₹55 to ₹200 depending on age).",
            "Sign the enrollment and nomination form.",
            "Receive your unique Shram Yogi Pension Card."
        ],
        "official_portal": "https://maandhan.in"
    },

    # 💰 Financial Inclusion (3 schemes)
    {
        "id": "jan_dhan",
        "name": "Pradhan Mantri Jan Dhan Yojana (PMJDY)",
        "category": "Financial Inclusion",
        "benefits": "Provides a zero-balance bank account, a RuPay debit card, free ₹2 Lakh accidental insurance cover, and an overdraft facility of up to ₹10,000.",
        "eligibility_rules": {
            "min_age": 10,
            "max_age": 120,
            "max_income": None,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["All"],
            "disability_required": False
        },
        "description": "PMJDY is a national mission for financial inclusion to ensure access to financial services like banking savings accounts, credit, insurance, and pensions in an affordable manner.",
        "required_documents": [
            "Aadhaar Card or Voter ID Card",
            "Address Proof (if different from ID)",
            "Two Passport Size Photographs"
        ],
        "application_steps": [
            "Visit any nationalized or private commercial bank branch or Bank Mitra kiosk.",
            "Ask for the Jan Dhan Account opening form.",
            "Fill in identity, address, and nominee details.",
            "Submit the form along with Aadhaar photocopy and photos.",
            "Receive your zero-balance bank passbook and RuPay debit card."
        ],
        "official_portal": "https://pmjdy.gov.in"
    },
    {
        "id": "combined_insurance",
        "name": "PM Jeevan Jyoti Bima + Suraksha Bima Combined Plan",
        "category": "Financial Inclusion",
        "benefits": "Provides a combined insurance cover of ₹4 Lakh (₹2 Lakh life insurance + ₹2 Lakh accidental insurance) for a total premium of ₹456 per year.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 50,
            "max_income": None,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["All"],
            "disability_required": False
        },
        "description": "A combined social security pack linking both PMSBY and PMJJBY schemes directly to Jan Dhan savings accounts for simplified auto-debit payments.",
        "required_documents": [
            "Aadhaar Card",
            "Jan Dhan Bank Account details",
            "Auto-debit authorization form"
        ],
        "application_steps": [
            "Visit the bank branch holding your Jan Dhan account.",
            "Request the combined Jan Suraksha enrollment package.",
            "Fill in nominee, age, and Aadhaar details.",
            "Check the auto-debit option for both PMJJBY and PMSBY.",
            "Ensure a minimum balance of ₹456 is in the account every May."
        ],
        "official_portal": "https://jansuraksha.gov.in"
    },
    {
        "id": "standup_sc_st",
        "name": "Stand-Up India Scheme for SC/ST Entrepreneurs",
        "category": "Financial Inclusion",
        "benefits": "Provides bank loans between ₹10 Lakh and ₹1 Crore for setting up a greenfield business in manufacturing, services, or trading.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 120,
            "max_income": None,
            "gender": "All",
            "states": ["All"],
            "caste": ["SC", "ST"],
            "occupation": ["Entrepreneur"],
            "disability_required": False
        },
        "description": "Stand-Up India aims to support Scheduled Caste (SC) and Scheduled Tribe (ST) communities in becoming business owners and creating new job opportunities.",
        "required_documents": [
            "Aadhaar Card & PAN Card",
            "Caste Certificate (SC/ST)",
            "Greenfield Project Business Proposal",
            "Proof of Business Address",
            "Venture details and KYC"
        ],
        "application_steps": [
            "Go to the Stand-Up India Portal (standupmitra.in) or approach a commercial bank branch.",
            "Register as a SC/ST borrower.",
            "Submit the business proposal and upload the caste certificate.",
            "Select banks to process your request.",
            "The bank verifies eligibility, reviews the proposal, and sanctions the loan."
        ],
        "official_portal": "https://www.standupmitra.in"
    },

    # 📡 Digital & Others (3 schemes)
    {
        "id": "pm_wani",
        "name": "PM Wani (Public WiFi Access Network)",
        "category": "Digital Services",
        "benefits": "Provides all citizens with high-speed, affordable public WiFi internet access at local shops and public hotspots across India without pre-registration.",
        "eligibility_rules": {
            "min_age": 0,
            "max_age": 120,
            "max_income": None,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["All"],
            "disability_required": False
        },
        "description": "PM-WANI (WiFi Access Network Interface) aims to democratize broadband internet delivery across the country through local Public Data Offices (PDOs).",
        "required_documents": [
            "None (Requires only a mobile number for OTP login)"
        ],
        "application_steps": [
            "Walk into any PM-WANI enabled WiFi hotspot zone (usually marked by local grocery/recharge shops).",
            "Open WiFi settings on your phone and connect to the PM-WANI network.",
            "Enter your mobile number on the login page.",
            "Enter the OTP received via SMS to access high-speed internet."
        ],
        "official_portal": "https://sarathsanchar.gov.in"
    },
    {
        "id": "digilocker",
        "name": "DigiLocker Digital Wallet",
        "category": "Digital Services",
        "benefits": "Provides a secure cloud storage account to store, verify, and share official digital documents (driving license, marksheets, PAN), eliminating physical paperwork.",
        "eligibility_rules": {
            "min_age": 5,
            "max_age": 120,
            "max_income": None,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["All"],
            "disability_required": False
        },
        "description": "DigiLocker is a flagship initiative of Ministry of Electronics & IT (MeitY) under the Digital India corporation, providing citizens with digital access to original issuer-verified documents.",
        "required_documents": [
            "Aadhaar Card",
            "Mobile number linked with Aadhaar"
        ],
        "application_steps": [
            "Download the DigiLocker App or go to digilocker.gov.in.",
            "Sign up using your name, date of birth, mobile number, and Aadhaar number.",
            "Verify using the Aadhaar OTP sent to your phone.",
            "Set a 6-digit security PIN.",
            "Search for your document issuers (e.g. CBSE, Income Tax, RTO) and pull your verified documents directly into your wallet."
        ],
        "official_portal": "https://digilocker.gov.in"
    },
    {
        "id": "csc",
        "name": "Common Service Centres (CSC)",
        "category": "Digital Services",
        "benefits": "Provides citizens in rural areas with direct access to over 300+ government, financial, utility, and education services at a single local point.",
        "eligibility_rules": {
            "min_age": 0,
            "max_age": 120,
            "max_income": None,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["All"],
            "disability_required": False
        },
        "description": "CSCs are the access points for delivery of essential public utility services, social welfare schemes, healthcare, financial, education, and agriculture services in rural villages.",
        "required_documents": [
            "Dependent on the specific scheme or service requested at the centre (Aadhaar is generally required)"
        ],
        "application_steps": [
            "Locate the nearest CSC in your village/town using the locator tool at csc.gov.in.",
            "Visit the centre with your Aadhaar and scheme requirements.",
            "The CSC operator submits your application on the government portal online.",
            "Pay the nominal service fee (if applicable).",
            "Collect the certificate, transaction slip, or printed card."
        ],
        "official_portal": "https://csc.gov.in"
    },
    {
        "id": "pm_surya_ghar",
        "name": "PM Surya Ghar: Muft Bijli Yojana",
        "category": "Housing",
        "benefits": "Provides free electricity (up to 300 units/month) for households and solar panel installation subsidies up to ₹78,000.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 120,
            "max_income": None,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["All"],
            "disability_required": False
        },
        "description": "A central sector scheme promoting rooftop solar installations on residential houses to provide free electricity to 1 crore households across India.",
        "required_documents": [
            "Aadhaar Card",
            "Electricity Bill (Active Consumer Number)",
            "Bank Account Passbook Copy",
            "Proof of Roof Ownership or NOC"
        ],
        "application_steps": [
            "Register on the National Portal for Rooftop Solar (pmsuryaghar.gov.in) with mobile number and electricity consumer ID.",
            "Apply for Rooftop Solar installation.",
            "Wait for feasibility approval from the local distribution company (DISCOM).",
            "Install the solar panels through any of the DISCOM-registered vendors.",
            "Submit installation details and apply for a net meter.",
            "DISCOM installs the net meter and inspects the site.",
            "Once approved, a commissioning certificate is generated, and the subsidy is credited to your bank account."
        ],
        "official_portal": "https://pmsuryaghar.gov.in"
    },
    {
        "id": "pm_vishwakarma",
        "name": "PM Vishwakarma Scheme",
        "category": "Employment & Skill",
        "benefits": "Provides collateral-free loans up to ₹3 Lakh (at 5% interest rate), basic and advanced skill training with a daily stipend of ₹500, a toolkit incentive of ₹15,000, and marketing support.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 120,
            "max_income": None,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["Labourer", "Entrepreneur"],
            "disability_required": False
        },
        "description": "A central scheme designed to support traditional artisans and craftspeople (carpenters, potters, blacksmiths, weavers, etc.) by upgrading their skills and scaling their business.",
        "required_documents": [
            "Aadhaar Card",
            "Mobile number linked with Aadhaar",
            "Bank Passbook copy",
            "Caste/Category Certificate (if applicable)",
            "Proof of engagement in one of the 18 traditional trades"
        ],
        "application_steps": [
            "Go to the PM Vishwakarma Portal (pmvishwakarma.gov.in) or visit the nearest Common Service Centre (CSC).",
            "Authenticate using Aadhaar biometric details.",
            "Fill in the registration form with personal and trade details.",
            "The application undergoes a 3-step verification (Gram Panchayat/ULB level, District Committee level, and Screening Committee level).",
            "Upon successful verification, download the PM Vishwakarma Digital ID Card and Certificate.",
            "Enroll in basic training and claim the toolkit incentive.",
            "Apply for the first tranche of loan (₹1 Lakh) after training."
        ],
        "official_portal": "https://pmvishwakarma.gov.in"
    },
    {
        "id": "lakhpati_didi",
        "name": "Lakhpati Didi Scheme",
        "category": "Women Empowerment",
        "benefits": "Provides skill training in drone piloting, LED bulb making, plumbing, tailoring, etc., along with financial assistance, business guidance, and access to interest-free loans to help women SHG members earn at least ₹1 Lakh per year.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 65,
            "max_income": 100000,
            "gender": "Female",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["Farmer", "Labourer", "Entrepreneur", "Other"],
            "disability_required": False
        },
        "description": "A central government initiative to empower rural women by supporting them to form Self-Help Groups (SHGs) and start micro-enterprises, raising their household income to at least ₹1 Lakh annually.",
        "required_documents": [
            "Aadhaar Card",
            "Self-Help Group (SHG) membership certificate or registration number",
            "Income Certificate",
            "Bank Account Passbook copy",
            "Proof of Residence"
        ],
        "application_steps": [
            "Connect with your local Self-Help Group (SHG) leader or block DAY-NRLM office.",
            "Provide personal details and specify the trade/skill you want training for (e.g. drone pilot, tailoring).",
            "Submit the application form with Aadhaar and SHG membership proof.",
            "Participate in the designated vocational training and financial literacy programs.",
            "Receive business setup support and seed capital/microfinance loans from the bank linked to your SHG."
        ],
        "official_portal": "https://nrlm.gov.in"
    },
    {
        "id": "pmbjp",
        "name": "Pradhan Mantri Bhartiya Janaushadhi Pariyojana (PMBJP)",
        "category": "Health",
        "benefits": "Provides high-quality generic medicines, surgical materials, and wellness products at 50% to 90% cheaper prices than branded counterparts.",
        "eligibility_rules": {
            "min_age": 0,
            "max_age": 120,
            "max_income": None,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["All"],
            "disability_required": False
        },
        "description": "PMBJP is a campaign launched by the Department of Pharmaceuticals to provide affordable quality medicines to all Indian citizens through dedicated outlets called PM Bhartiya Janaushadhi Kendras.",
        "required_documents": [
            "Doctor's Prescription (only required to purchase prescription generic drugs at the store; no documents needed to visit or browse the stores)"
        ],
        "application_steps": [
            "Locate your nearest PM Bhartiya Janaushadhi Kendra online or via the mobile app.",
            "Visit the store with a valid doctor's prescription for the required medicines.",
            "Purchase the generic equivalents at highly subsidized rates.",
            "Keep the receipt for billing and records."
        ],
        "official_portal": "http://janaushadhi.gov.in"
    },
    {
        "id": "igndps",
        "name": "Indira Gandhi National Disability Pension Scheme (IGNDPS)",
        "category": "Senior Citizens",
        "benefits": "Provides a monthly pension of ₹300 (for ages 18-79) and ₹500 (for age 80+) to persons with severe or multiple disabilities who are below the poverty line.",
        "eligibility_rules": {
            "min_age": 18,
            "max_age": 79,
            "max_income": 100000,
            "gender": "All",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["All"],
            "disability_required": True
        },
        "description": "A non-contributory central pension scheme under the National Social Assistance Programme (NSAP) providing social security and monthly cash transfers to severely disabled BPL citizens.",
        "required_documents": [
            "Aadhaar Card",
            "Disability Certificate issued by a Government Medical Board showing 80% or more disability",
            "BPL Ration Card or Income Certificate",
            "Bank Account Passbook copy",
            "Passport Size Photograph"
        ],
        "application_steps": [
            "Obtain the NSAP application form from the local Gram Panchayat office (for rural) or Municipal Corporation (for urban).",
            "Fill in the applicant details and select IGNDPS.",
            "Attach the Disability Certificate and BPL Ration card.",
            "Submit the application to the Block Development Officer (BDO) or Social Welfare Officer.",
            "Once the verification is complete, the pension is approved and credited directly to the bank account."
        ],
        "official_portal": "https://nsap.nic.in"
    },
    {
        "id": "ignwps",
        "name": "Indira Gandhi National Widow Pension Scheme (IGNWPS)",
        "category": "Women Empowerment",
        "benefits": "Provides a monthly pension of ₹300 (for ages 40-79) and ₹500 (for age 80+) to widows living below the poverty line.",
        "eligibility_rules": {
            "min_age": 40,
            "max_age": 79,
            "max_income": 100000,
            "gender": "Female",
            "states": ["All"],
            "caste": ["All"],
            "occupation": ["All"],
            "disability_required": False
        },
        "description": "A non-contributory central pension scheme under the National Social Assistance Programme (NSAP) providing social security and monthly financial aid to poor widows in India.",
        "required_documents": [
            "Aadhaar Card",
            "Death Certificate of the Husband",
            "BPL Ration Card or Income Certificate",
            "Bank Account Passbook copy",
            "Passport Size Photograph"
        ],
        "application_steps": [
            "Obtain the NSAP application form from the local Gram Panchayat or Municipal Corporation.",
            "Fill in personal and family details and select IGNWPS.",
            "Attach the husband's death certificate and BPL Ration card.",
            "Submit the form to the Social Welfare Department office or block office.",
            "Following verification of BPL and widow status, the pension is credited monthly to your bank account."
        ],
        "official_portal": "https://nsap.nic.in"
    }
]

# Write to schemes.json
schemes_json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "schemes.json")
os.makedirs(os.path.dirname(schemes_json_path), exist_ok=True)

with open(schemes_json_path, "w", encoding="utf-8") as f:
    json.dump(full_schemes, f, indent=2, ensure_ascii=False)

print("Successfully generated full schemes dataset with 54 schemes at data/schemes.json!")
