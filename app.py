import sys
import csv
from flask import Flask, request, render_template, redirect
import sqlite3
import os
import requests
from bs4 import BeautifulSoup
from transformers import pipeline
import spacy
from collections import Counter
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
model = MBartForConditionalGeneration.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")
tokenizer = MBart50TokenizerFast.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")

# Set the source and target languages
tokenizer.src_lang = "en_XX"  # English
target_lang = "hi_IN"  # Hindi

app = Flask(__name__)

# SQLite database setup
DATABASE = 'data.db'

# Initialize spaCy for keyword extraction
nlp = spacy.load("en_core_web_sm")
ner = pipeline("ner", grouped_entities=True)

# Initialize Hugging Face summarization pipeline
summarizer = pipeline("summarization")
keyword_to_topic = {
        # Politics and Government
        "election": "Politics",
        "vote": "Politics",
        "government": "Politics",
        "parliament": "Politics",
        "prime minister": "Politics",
        "president": "Politics",
        "political party": "Politics",
        "election results": "Politics",
        "voting": "Politics",
        "democracy": "Politics",
        "cabinet": "Politics",
        "policy": "Politics",
        "law": "Politics",
        "bill": "Politics",
        "senate": "Politics",
        "congress": "Politics",
        "opposition": "Politics",
        "coalition": "Politics",
        "protest": "Politics",
        "strike": "Politics",
        "rally": "Politics",
        "campaign": "Politics",
        "candidate": "Politics",
        "election commission": "Politics",

        # Disasters and Accidents
        "flood": "Disasters",
        "earthquake": "Disasters",
        "cyclone": "Disasters",
        "tsunami": "Disasters",
        "landslide": "Disasters",
        "fire": "Disasters",
        "accident": "Disasters",
        "crash": "Disasters",
        "explosion": "Disasters",
        "storm": "Disasters",
        "hurricane": "Disasters",
        "tornado": "Disasters",
        "drought": "Disasters",
        "famine": "Disasters",
        "heatwave": "Disasters",
        "cold wave": "Disasters",
        "avalanche": "Disasters",
        "volcano": "Disasters",
        "rescue": "Disasters",
        "relief": "Disasters",
        "emergency": "Disasters",
        "evacuation": "Disasters",

        # Sports
        "cricket": "Sports",
        "football": "Sports",
        "soccer": "Sports",
        "tennis": "Sports",
        "olympics": "Sports",
        "world cup": "Sports",
        "match": "Sports",
        "tournament": "Sports",
        "championship": "Sports",
        "player": "Sports",
        "team": "Sports",
        "score": "Sports",
        "goal": "Sports",
        "stadium": "Sports",
        "coach": "Sports",
        "training": "Sports",
        "injury": "Sports",
        "victory": "Sports",
        "defeat": "Sports",
        "medal": "Sports",
        "athlete": "Sports",
        "sportsmanship": "Sports",

        # Technology
        "technology": "Technology",
        "innovation": "Technology",
        "smartphone": "Technology",
        "laptop": "Technology",
        "computer": "Technology",
        "internet": "Technology",
        "5G": "Technology",
        "AI": "Technology",
        "artificial intelligence": "Technology",
        "machine learning": "Technology",
        "robotics": "Technology",
        "cybersecurity": "Technology",
        "hacking": "Technology",
        "data breach": "Technology",
        "software": "Technology",
        "app": "Technology",
        "startup": "Technology",
        "gadget": "Technology",
        "drone": "Technology",
        "blockchain": "Technology",
        "cryptocurrency": "Technology",
        "bitcoin": "Technology",
        "ethereum": "Technology",
        "NFT": "Technology",
        "virtual reality": "Technology",
        "augmented reality": "Technology",

        # Entertainment
        "movie": "Entertainment",
        "film": "Entertainment",
        "actor": "Entertainment",
        "actress": "Entertainment",
        "director": "Entertainment",
        "bollywood": "Entertainment",
        "hollywood": "Entertainment",
        "music": "Entertainment",
        "song": "Entertainment",
        "album": "Entertainment",
        "concert": "Entertainment",
        "festival": "Entertainment",
        "award": "Entertainment",
        "oscar": "Entertainment",
        "grammy": "Entertainment",
        "television": "Entertainment",
        "TV show": "Entertainment",
        "series": "Entertainment",
        "celebrity": "Entertainment",
        "gossip": "Entertainment",
        "fashion": "Entertainment",
        "red carpet": "Entertainment",
        "premiere": "Entertainment",

        # Business and Economy
        "economy": "Business",
        "business": "Business",
        "market": "Business",
        "stock": "Business",
        "share": "Business",
        "investment": "Business",
        "trade": "Business",
        "export": "Business",
        "import": "Business",
        "GDP": "Business",
        "inflation": "Business",
        "unemployment": "Business",
        "bank": "Business",
        "finance": "Business",
        "tax": "Business",
        "budget": "Business",
        "recession": "Business",
        "startup": "Business",
        "entrepreneur": "Business",
        "profit": "Business",
        "loss": "Business",
        "merger": "Business",
        "acquisition": "Business",
        "IPO": "Business",

        # Health and Medicine
        "health": "Health",
        "medicine": "Health",
        "hospital": "Health",
        "doctor": "Health",
        "patient": "Health",
        "vaccine": "Health",
        "COVID": "Health",
        "pandemic": "Health",
        "epidemic": "Health",
        "disease": "Health",
        "virus": "Health",
        "infection": "Health",
        "treatment": "Health",
        "surgery": "Health",
        "mental health": "Health",
        "fitness": "Health",
        "nutrition": "Health",
        "diet": "Health",
        "exercise": "Health",
        "wellness": "Health",
        "pharmacy": "Health",
        "clinical trial": "Health",

        # Education
        "education": "Education",
        "school": "Education",
        "college": "Education",
        "university": "Education",
        "student": "Education",
        "teacher": "Education",
        "exam": "Education",
        "result": "Education",
        "admission": "Education",
        "scholarship": "Education",
        "degree": "Education",
        "course": "Education",
        "online learning": "Education",
        "literacy": "Education",
        "research": "Education",
        "thesis": "Education",
        "academic": "Education",
        "curriculum": "Education",
        "tuition": "Education",
        "campus": "Education",
        "alumni": "Education",

        # Environment
        "environment": "Environment",
        "climate change": "Environment",
        "global warming": "Environment",
        "pollution": "Environment",
        "deforestation": "Environment",
        "wildlife": "Environment",
        "conservation": "Environment",
        "recycling": "Environment",
        "sustainability": "Environment",
        "green energy": "Environment",
        "solar power": "Environment",
        "wind energy": "Environment",
        "carbon emissions": "Environment",
        "ecosystem": "Environment",
        "biodiversity": "Environment",
        "natural disaster": "Environment",
        "renewable energy": "Environment",
        "plastic waste": "Environment",
        "air quality": "Environment",
        "water conservation": "Environment",

        # Crime and Law
        "crime": "Crime",
        "murder": "Crime",
        "theft": "Crime",
        "robbery": "Crime",
        "fraud": "Crime",
        "scam": "Crime",
        "kidnapping": "Crime",
        "arrest": "Crime",
        "police": "Crime",
        "investigation": "Crime",
        "court": "Crime",
        "judge": "Crime",
        "verdict": "Crime",
        "sentence": "Crime",
        "prison": "Crime",
        "jail": "Crime",
        "bail": "Crime",
        "lawyer": "Crime",
        "trial": "Crime",
        "evidence": "Crime",
        "witness": "Crime",
        "gang": "Crime",
        "terrorism": "Crime",
        "cybercrime": "Crime",

        # Science and Research
        "science": "Science",
        "research": "Science",
        "discovery": "Science",
        "experiment": "Science",
        "space": "Science",
        "NASA": "Science",
        "astronomy": "Science",
        "physics": "Science",
        "chemistry": "Science",
        "biology": "Science",
        "genetics": "Science",
        "evolution": "Science",
        "innovation": "Science",
        "invention": "Science",
        "scientist": "Science",
        "lab": "Science",
        "theory": "Science",
        "hypothesis": "Science",
        "publication": "Science",
        "journal": "Science",
        "peer review": "Science",
        "climate science": "Science",
        "environmental science": "Science",

        # Miscellaneous
        "festival": "Miscellaneous",
        "celebration": "Miscellaneous",
        "event": "Miscellaneous",
        "holiday": "Miscellaneous",
        "travel": "Miscellaneous",
        "tourism": "Miscellaneous",
        "culture": "Miscellaneous",
        "tradition": "Miscellaneous",
        "religion": "Miscellaneous",
        "festival": "Miscellaneous",
        "art": "Miscellaneous",
        "literature": "Miscellaneous",
        "history": "Miscellaneous",
        "archaeology": "Miscellaneous",
        "museum": "Miscellaneous",
        "heritage": "Miscellaneous",
        "monument": "Miscellaneous",
        "festival": "Miscellaneous",
}
states_and_districts = {
        "Andhra Pradesh": ["Anantapur", "Chittoor", "East Godavari", "Guntur", "Krishna", "Kurnool", "Prakasam", "Srikakulam", "Sri Potti Sriramulu Nellore", "Visakhapatnam", "Vizianagaram", "West Godavari", "YSR Kadapa"],
        "Arunachal Pradesh": ["Anjaw", "Changlang", "Dibang Valley", "East Kameng", "East Siang", "Kamle", "Kra Daadi", "Kurung Kumey", "Lepa Rada", "Lohit", "Longding", "Lower Dibang Valley", "Lower Siang", "Lower Subansiri", "Namsai", "Pakke Kessang", "Papum Pare", "Shi Yomi", "Siang", "Tawang", "Tirap", "Upper Dibang Valley", "Upper Siang", "Upper Subansiri", "West Kameng", "West Siang"],
        "Assam": ["Baksa", "Barpeta", "Biswanath", "Bongaigaon", "Cachar", "Charaideo", "Chirang", "Darrang", "Dhemaji", "Dhubri", "Dibrugarh", "Dima Hasao", "Goalpara", "Golaghat", "Hailakandi", "Hojai", "Jorhat", "Kamrup", "Kamrup Metropolitan", "Karbi Anglong", "Karimganj", "Kokrajhar", "Lakhimpur", "Majuli", "Morigaon", "Nagaon", "Nalbari", "Sivasagar", "Sonitpur", "South Salmara-Mankachar", "Tinsukia", "Udalguri", "West Karbi Anglong"],
        "Bihar": ["Araria", "Arwal", "Aurangabad", "Banka", "Begusarai", "Bhagalpur", "Bhojpur", "Buxar", "Darbhanga", "East Champaran", "Gaya", "Gopalganj", "Jamui", "Jehanabad", "Kaimur", "Katihar", "Khagaria", "Kishanganj", "Lakhisarai", "Madhepura", "Madhubani", "Munger", "Muzaffarpur", "Nalanda","Purnia", "Rohtas", "Saharsa", "Samastipur", "Saran", "Sheikhpura", "Sheohar", "Sitamarhi", "Siwan","Patna", "Supaul", "Vaishali", "West Champaran"],
        "Chhattisgarh": ["Balod", "Baloda Bazar", "Balrampur", "Bastar", "Bemetara", "Bijapur", "Bilaspur", "Dantewada", "Dhamtari", "Durg", "Gariyaband", "Janjgir-Champa", "Jashpur", "Kabirdham", "Kanker", "Kondagaon", "Korba","Korea", "Mahasamund", "Mungeli", "Narayanpur", "Raigarh", "Raipur", "Rajnandgaon", "Sukma", "Surajpur", "Surguja"],
        "Delhi": ["Central Delhi", "East Delhi", "New Delhi", "North Delhi", "North East Delhi", "North West Delhi", "Shahdara", "South Delhi", "South East Delhi", "South West Delhi", "West Delhi","Delhi"],
        "Goa": ["North Goa", "South Goa"],
        "Gujarat": [ "Ahmedabad", "Amreli", "Anand", "Aravalli", "Banaskantha", "Bharuch", "Bhavnagar", "Botad", "Chhota Udaipur", "Dahod", "Dang", "Devbhoomi Dwarka", "Gandhinagar", "Gir Somnath", "Jamnagar", "Junagadh", "Kheda", "Kutch", "Mahisagar", "Mehsana", "Morbi", "Narmada", "Navsari", "Panchmahal", "Patan", "Porbandar", "Rajkot", "Sabarkantha", "Surat", "Surendranagar", "Tapi", "Vadodara", "Valsad"],
        "Haryana": ["Ambala", "Bhiwani", "Charkhi Dadri", "Faridabad", "Fatehabad", "Gurugram", "Hisar", "Jhajjar", "Jind", "Kaithal", "Karnal", "Kurukshetra", "Mahendragarh", "Nuh", "Palwal", "Panchkula", "Panipat", "Rewari", "Rohtak", "Sirsa", "Sonipat", "Yamunanagar"],
        "Himachal Pradesh": ["Bilaspur", "Chamba", "Hamirpur", "Kangra", "Kinnaur", "Kullu", "Lahaul and Spiti", "Mandi", "Shimla", "Sirmaur", "Solan", "Una"],
        "Jammu and Kashmir": ["Anantnag", "Bandipora", "Baramulla", "Budgam", "Doda", "Ganderbal", "Jammu", "Kathua", "Kishtwar", "Kulgam", "Kupwara", "Poonch", "Pulwama", "Rajouri", "Ramban", "Reasi", "Samba", "Shopian", "Srinagar", "Udhampur"],
        "Jharkhand": ["Bokaro", "Chatra", "Deoghar", "Dhanbad", "Dumka", "East Singhbhum", "Garhwa", "Giridih", "Godda", "Gumla", "Hazaribagh", "Jamtara", "Khunti", "Koderma", "Latehar", "Lohardaga", "Pakur", "Palamu", "Ramgarh", "Ranchi", "Sahibganj", "Seraikela Kharsawan", "Simdega", "West Singhbhum"],
        "Kerala": ["Alappuzha", "Ernakulam", "Idukki", "Kannur", "Kasaragod", "Kollam", "Kottayam", "Kozhikode", "Malappuram", "Palakkad", "Pathanamthitta", "Thiruvananthapuram", "Thrissur", "Wayanad"],
        "Karnataka": ["Bagalkot", "Ballari", "Belagavi", "Bengaluru Rural", "Bengaluru Urban", "Bidar", "Chamarajanagar", "Chikkaballapur", "Chikkamagaluru", "Chitradurga", "Dakshina Kannada", "Davanagere", "Dharwad", "Gadag", "Hassan", "Haveri", "Kalaburagi", "Kodagu", "Kolar", "Koppal", "Mandya", "Mysuru", "Raichur", "Ramanagara", "Shivamogga", "Tumakuru", "Udupi", "Uttara Kannada", "Vijayapura", "Yadgir"],
        "Ladakh": ["Kargil", "Leh"],
        "Madhya Pradesh": ["Agar Malwa", "Alirajpur", "Anuppur", "Ashoknagar", "Balaghat", "Barwani", "Betul", "Bhind", "Bhopal", "Burhanpur", "Chhatarpur", "Chhindwara", "Damoh", "Datia", "Dewas", "Dhar", "Dindori", "Guna", "Gwalior", "Harda", "Hoshangabad", "Indore", "Jabalpur", "Jhabua", "Katni", "Khandwa", "Khargone", "Mandla", "Mandsaur", "Morena", "Narsinghpur", "Neemuch", "Panna", "Raisen", "Rajgarh", "Ratlam", "Rewa", "Sagar", "Satna", "Sehore", "Seoni", "Shahdol", "Shajapur", "Sheopur", "Shivpuri", "Sidhi", "Singrauli", "Tikamgarh", "Ujjain", "Umaria", "Vidisha"],
        "Maharashtra": ["Ahmednagar", "Akola", "Amravati", "Aurangabad", "Beed", "Bhandara", "Buldhana", "Chandrapur", "Dhule", "Gadchiroli", "Gondia", "Hingoli", "Jalgaon", "Jalna", "Kolhapur", "Latur", "Mumbai", "Mumbai Suburban", "Nagpur", "Nanded", "Nandurbar", "Nashik", "Osmanabad", "Palghar", "Parbhani", "Pune", "Raigad", "Ratnagiri", "Sangli", "Satara", "Sindhudurg", "Solapur", "Thane", "Wardha", "Washim", "Yavatmal"],
        "Manipur": ["Bishnupur", "Chandel", "Churachandpur", "Imphal East", "Imphal West", "Jiribam", "Kakching", "Kamjong", "Kangpokpi", "Noney", "Pherzawl", "Senapati", "Tamenglong", "Tengnoupal", "Thoubal", "Ukhrul"],
        "Meghalaya": ["East Garo Hills", "East Jaintia Hills", "East Khasi Hills", "North Garo Hills", "Ri Bhoi", "South Garo Hills", "South West Garo Hills", "South West Khasi Hills", "West Garo Hills", "West Jaintia Hills", "West Khasi Hills"],
        "Mizoram": ["Aizawl", "Champhai", "Hnahthial", "Khawzawl", "Kolasib", "Lawngtlai", "Lunglei", "Mamit", "Saiha", "Saitual", "Serchhip"],
        "Nagaland": ["Chümoukedima", "Dimapur", "Kiphire", "Kohima", "Longleng", "Mokokchung", "Mon", "Niuland", "Noklak", "Peren", "Phek", "Shamator", "Tseminyü", "Tuensang", "Wokha", "Zünheboto"],
        "Odisha": ["Angul", "Balangir", "Balasore", "Bargarh", "Bhadrak", "Boudh", "Cuttack", "Deogarh", "Dhenkanal", "Gajapati", "Ganjam", "Jagatsinghpur", "Jajpur", "Jharsuguda", "Kalahandi", "Kandhamal", "Kendrapara", "Kendujhar", "Khordha", "Koraput", "Malkangiri", "Mayurbhanj", "Nabarangpur", "Nayagarh", "Nuapada", "Puri", "Rayagada", "Sambalpur", "Subarnapur", "Sundargarh"],
        "Puducherry": ["Karaikal", "Mahe", "Puducherry", "Yanam"],
        "Punjab": ["Amritsar", "Barnala", "Bathinda", "Faridkot", "Fatehgarh Sahib", "Fazilka", "Ferozepur", "Gurdaspur", "Hoshiarpur", "Jalandhar", "Kapurthala", "Ludhiana", "Mansa", "Moga", "Mohali", "Muktsar", "Pathankot", "Patiala", "Rupnagar", "Sangrur", "Shaheed Bhagat Singh Nagar", "Tarn Taran"],
        "Rajasthan": ["Ajmer", "Alwar", "Banswara", "Baran", "Barmer", "Bharatpur", "Bhilwara", "Bikaner", "Bundi", "Chittorgarh", "Churu", "Dausa", "Dholpur", "Dungarpur", "Hanumangarh", "Jaipur", "Jaisalmer", "Jalore", "Jhalawar", "Jhunjhunu", "Jodhpur", "Karauli", "Kota", "Nagaur", "Pali", "Pratapgarh", "Rajsamand", "Sawai Madhopur", "Sikar", "Sirohi", "Sri Ganganagar", "Tonk", "Udaipur"],
        "Sikkim": ["East Sikkim", "North Sikkim", "South Sikkim", "West Sikkim"],
        "Tamil Nadu": ["Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore", "Dharmapuri", "Dindigul", "Erode", "Kallakurichi", "Kanchipuram", "Kanyakumari", "Karur", "Krishnagiri", "Madurai", "Mayiladuthurai", "Nagapattinam", "Namakkal", "Nilgiris", "Perambalur", "Pudukkottai", "Ramanathapuram", "Ranipet", "Salem", "Sivaganga", "Tenkasi", "Thanjavur", "Theni", "Thoothukudi", "Tiruchirappalli", "Tirunelveli", "Tirupathur", "Tiruppur", "Tiruvallur", "Tiruvannamalai", "Tiruvarur", "Vellore", "Viluppuram", "Virudhunagar"],
        "Telangana": ["Adilabad", "Bhadradri Kothagudem", "Hyderabad", "Jagtial", "Jangaon", "Jayashankar Bhupalpally", "Jogulamba Gadwal", "Kamareddy", "Karimnagar", "Khammam", "Komaram Bheem Asifabad", "Mahabubabad", "Mahabubnagar", "Mancherial", "Medak", "Medchal-Malkajgiri", "Mulugu", "Nagarkurnool", "Nalgonda", "Nirmal", "Nizamabad", "Peddapalli", "Rajanna Sircilla", "Rangareddy", "Sangareddy", "Siddipet", "Suryapet", "Vikarabad", "Wanaparthy", "Warangal Rural", "Warangal Urban", "Yadadri Bhuvanagiri"],
        "Tripura": ["Dhalai", "Gomati", "Khowai", "North Tripura", "Sepahijala", "South Tripura", "Unakoti", "West Tripura"],
        "Uttar Pradesh": ["Agra", "Aligarh", "Ambedkar Nagar", "Amethi", "Amroha", "Auraiya", "Ayodhya", "Azamgarh", "Baghpat", "Bahraich", "Ballia", "Balrampur", "Banda", "Barabanki", "Bareilly", "Basti", "Bhadohi", "Bijnor", "Budaun", "Bulandshahr", "Chandauli", "Chitrakoot", "Deoria", "Etah", "Etawah", "Farrukhabad", "Fatehpur", "Firozabad", "Gautam Buddha Nagar", "Ghaziabad", "Ghazipur", "Gonda", "Gorakhpur", "Hamirpur", "Hapur", "Hardoi", "Hathras", "Jalaun", "Jaunpur", "Jhansi", "Kannauj", "Kanpur Dehat", "Kanpur Nagar", "Kasganj", "Kaushambi", "Kushinagar", "Lakhimpur Kheri", "Lalitpur", "Lucknow", "Maharajganj", "Mahoba", "Mainpuri", "Mathura", "Mau", "Meerut", "Mirzapur", "Moradabad", "Muzaffarnagar", "Pilibhit", "Pratapgarh", "Prayagraj", "Raebareli", "Rampur", "Saharanpur", "Sambhal", "Sant Kabir Nagar", "Shahjahanpur", "Shamli", "Shrawasti", "Siddharthnagar", "Sitapur", "Sonbhadra", "Sultanpur", "Unnao", "Varanasi"],
        "Uttarakhand": ["Almora", "Bageshwar", "Chamoli", "Champawat", "Dehradun", "Haridwar", "Nainital", "Pauri Garhwal", "Pithoragarh", "Rudraprayag", "Tehri Garhwal", "Udham Singh Nagar", "Uttarkashi"],
        "West Bengal": ["Alipurduar", "Bankura", "Birbhum", "Cooch Behar", "Dakshin Dinajpur", "Darjeeling", "Hooghly", "Howrah", "Jalpaiguri", "Jhargram", "Kalimpong", "Kolkata", "Malda", "Murshidabad", "Nadia", "North 24 Parganas", "Paschim Bardhaman", "Paschim Medinipur", "Purba Bardhaman", "Purba Medinipur", "Purulia", "South 24 Parganas", "Uttar Dinajpur"]

}
# Function to scrape news articles
def scrape_news_1(url):
    """
    Scrape news articles from a given URL.
    """
    news_headlines=[]
    html_text=requests.get(url)
    if html_text.status_code != 200:
          print(f"Failed to fetch page. Status code: {html_text.status_code}")
          exit()
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_text.content, "html.parser")

    # Find the news headlines and links

    for article in soup.find_all('div',class_="iN5CR"):
      link =article.find("a")["href"]
      if link.startswith("/"):
        link="https://timesofindia.indiatimes.com"+link
      headline=article.find("div",class_="WavNE").text
      news_headlines.append({"headline":headline,"link":link})
    return news_headlines

def scrapy_news_2(url):
    """
    Scrape news articles from a given URL.
    """
    news_headlines=[]
    num_pages=9;

    for i in range(2,num_pages+1):

      url=f"{base_url}/{i}"
      html_text=requests.get(url)
      if html_text.status_code != 200:
            print(f"Failed to fetch page {i}. Status code: {html_text.status_code}")
            continue
      # Parse the HTML content using BeautifulSoup
      soup = BeautifulSoup(html_text.content, "html.parser")

    # Find the news headlines and links

    for article in soup.find_all('span',class_="w_tle"):
      link =article.find("a")["href"]
      if link.startswith("/"):
        link="https://timesofindia.indiatimes.com"+link
      headline=article.find("a")["title"]
      news_headlines.append({"headline":headline,"link":link})
    return news_headlines
# Function to classify topics and subtopics
def classify_topics_and_subtopics(text):
    """
    Classify topics and subtopics from the given text.
    """
    
    # Function to resolve ambiguous districts
    def resolve_ambiguity(headline, district):

        if "Maharashtra" in headline:
            return "Maharashtra"
        elif "Bihar" in headline:
            return "Bihar"
        else:
            return None

    def find_partial_match(text, districts):
        for district in districts:
            if district in text:
                return district
        return None       
    def classify_headline(item):
        headline=item['headline']
        doc = ner(headline)
        locations = [item['word'] for item in doc]

        for state, districts in states_and_districts.items():
            if state in headline:
                district = find_partial_match(headline, districts)

                if district == "Aurangabad":
                  resolved_state = resolve_ambiguity(headline, district)
                  if resolved_state:
                      return {"headline": headline, "state": resolved_state, "district": district}
                else:
                  return {"headline": headline,"link":item['link'], "state": state, "district": district}

                return {"headline": headline,"link":item['link'], "state": state, "district": None}

        # If no state is found, check for districts directly
        for state, districts in states_and_districts.items():
            district = find_partial_match(headline, districts)
            if district:
              if district == "Aurangabad":
                  resolved_state = resolve_ambiguity(headline, district)
                  if resolved_state:
                    return {"headline": headline,"link":item['link'], "state": resolved_state, "district": district}

              else:
                return {"headline": headline,"link":item['link'], "state": state, "district": district}

        return {"headline": headline,"link":item['link'], "state": None, "district": None}

# Function to get article text
def get_article_text(url):

  response=requests.get(url)

  if response.status_code == 200:
          soup = BeautifulSoup(response.content, "html.parser")
          content = soup.find("div", class_="_s30J clearfix")
          article_text = content.get_text(separator="\n").strip()
          return article_text
  else:
       
      return

# Function to summarize text
def summarize_text(text):
    """
    Summarize the given text using a pre-trained NLP model.
    """
    try: 
        summary = summarizer(text, max_length=max_length, min_length=20, do_sample=False)  # adjust max_length if needed
        return summary[0]['summary_text'] if summary else None
    except Exception as e:
         
        return None
# Function to extract keywords
def extract_keywords(text):
    """
    Extract keywords from the given text using spaCy.
    """
    doc = nlp(text)
    keywords = [token.text for token in doc if token.pos_ in ["NOUN", "PROPN"]]
    # return the top 5 most occuring keywords
    keywords = Counter(keywords).most_common(5)
    return keywords

# Funstion to get the topic
def get_topic(keywords):
    """
    Get the topic of the given headline.
    """
    for keyword in keywords:
        if keyword in keyword_to_topic:
            return keyword_to_topic[keyword]
    return "Miscellaneous"
# Function to generate SEO title
def generate_seo_title(headline, topic):
    return f"{headline} - {topic}"

# Function to generate meta description
def generate_meta_description(headline, summary):
    return f"{headline} - {summary}"

def translate_text(text):
    model_inputs = tokenizer(text, return_tensors="pt")
    generated_tokens = model.generate(
        **model_inputs,
        forced_bos_token_id=tokenizer.lang_code_to_id[target_lang]
    )
    translation = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
    return translation[0]
# Function to initialize the database
def init_db():
    if not os.path.exists(DATABASE):
        print("Database file does not exist. Creating a new one...")
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='csv_data'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("Creating 'csv_data' table...")
            cursor.execute('''
                CREATE TABLE csv_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    headline TEXT,
                    link TEXT,
                    state TEXT,
                    district TEXT,
                    article_text TEXT,
                    summary TEXT,
                    keywords TEXT,
                    topic TEXT,
                    seo_title TEXT,
                    meta_description TEXT
                )
            ''')
            conn.commit()
        else:
            print("Table 'csv_data' already exists.")

# Function to run the daily task
def daily_task():
    """
    Scrape, summarize, and store news articles daily.
    """
    
    articles_1= scrape_news_1('https://timesofindia.indiatimes.com/india')
    
    articles_2= scrapy_news_2('https://timesofindia.indiatimes.com/india')
    
    articles=articles_1+articles_2

    for article in articles:
        article=classify_headline(article)
         
    # remove the dict which having state =none
    articles=[item for item in articles if item['state'] is not None]

    # change the district to general news for those having none in district
    for item in articles:
      if item['district'] is None:
        item['district']="General News"

    # get the article text
    for item in articles:
    try:
        link = item['link']

        article_text = get_article_text(link)

        if article_text:
            item['article_text'] = article_text
        else:
            classified_headlines.remove(item)
             
    except Exception as e:
         
        classified_headlines.remove(item)
         
    # Get the articles 
    for item in articles:
        item['summary'] = summarize_text(item['article_text'])
    
     
    # removing the item which having none as a summary
    articles=[item for item in articles if item['summary'] is not None]
    
     
    # Extract keywords
     for item in articles:
        item['keywords'] = extract_keywords(item['summary'])
    
    # Extract topic
    for item in articles:
        item['topic'] = get_topic(item['keywords'])
    
    # Extract seo_titles
    for item in articles:
        item['seo_title'] = generate_seo_title(item['headline'], item['topic'])
    
    # Extract meta_descriptions
    for item in articles:
        item['meta_description'] = generate_meta_description(item['headline'],item['summary'])
     
    # Translate headline and summary
    for item in articles:
        item['headline_hi'] = translate_text(item['headline'])
        item['summary_hi'] = translate_text(item['summary'])
    
    # Store the articles in the database
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        for item in articles:
            cursor.execute('''
                INSERT INTO csv_data (
                    headline, link, state, district, article_text, 
                    summary, keywords, topic, seo_title, meta_description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item['headline'], item['link'], item['state'],item['district'],   
                item['article_text'], item['summary'], item['keywords'], item['topic'],item['seo_title'],item['meta_description'],item['headline_hi'],item['summary_hi']
            ))
        conn.commit()

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file uploaded", 400

    file = request.files['file']
    if file.filename == '':
        return "No file selected", 400

    if file and file.filename.endswith('.csv'):
        # Read CSV file
        csv_data = file.read().decode('utf-8').splitlines()
        csv_reader = csv.DictReader(csv_data)

        # Store each row in the SQLite database
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            for row in csv_reader:
                cursor.execute('''
                    INSERT INTO csv_data (
                        headline, link, state, district, article_text, 
                        summary, keywords, topic, seo_title, meta_description
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['headline'], row['link'], row['state'], row['district'], 
                    row['article_text'], row['summary'], row['keywords'], 
                    row['topic'], row['seo_title'], row['meta_description']
                ))
            conn.commit()

        return "File uploaded and data stored in database successfully!", 200
    else:
        return "Invalid file type. Please upload a CSV file.", 400

@app.route('/news')
def news_list():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, headline, summary, link FROM csv_data")
        news_items = cursor.fetchall()
    return render_template('news_list.html', news_items=news_items)

@app.route('/news/<int:news_id>')
def news_detail(news_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM csv_data WHERE id = ?", (news_id,))
        news_item = cursor.fetchone()
    if news_item:
        return render_template('news_detail.html', news_item=news_item)
    else:
        return "News article not found", 404

@app.route('/blog')
def blog():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM csv_data")
        articles = cursor.fetchall()
    return render_template('blog.html', articles=articles)

if __name__ == '__main__':
    if '--run-daily-task' in sys.argv:
        daily_task()
    else:
        init_db()
        app.run(debug=True)   
