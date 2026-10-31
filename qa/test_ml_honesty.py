#!/usr/bin/env python3
"""
Section 8: ML Honesty & Held-Out Benchmark Suite
Tests:
- Fresh, independently written held-out test set:
  10 scams and 10 legitimate messages per language/script:
  hi, hi_rom, bn, bn_rom, mr, mr_rom, kn, kn_rom, en (180 total samples)
- Evaluates real Precision, Recall, F1, and False Positive Rate (FPR)
- Compares to claimed numbers in MODEL_CARD.md
"""

import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.app.services.detector import detector

HELD_OUT_DATA = [
    # ========================== 1. HINDI (hi) ==========================
    # 10 Scams
    {"lang": "hi", "is_scam": 1, "cat": "ELECTRICITY_BILL", "text": "बिजली विभाग: आपका बिल बकाया है, आज रात 10 बजे लाइन काट दी जाएगी। कॉल करें 9876543210"},
    {"lang": "hi", "is_scam": 1, "cat": "FAKE_KYC", "text": "एसबीआई सेवा: आपका खाता 24 घंटे में ब्लॉक हो जाएगा। पैन लिंक करें: http://sbi-pan-update.xyz"},
    {"lang": "hi", "is_scam": 1, "cat": "UPI_COLLECT_FRAUD", "text": "पेटीएम रिवॉर्ड: आपको 4000 रुपये कैशबैक मिला है। प्राप्त करने के लिए यूपीआई पिन डालें।"},
    {"lang": "hi", "is_scam": 1, "cat": "LOTTERY_PRIZE", "text": "बधाई हो! आपका नंबर 15 लाख की मारुति सुजुकी लॉटरी में चुना गया है। संपर्क करें।"},
    {"lang": "hi", "is_scam": 1, "cat": "PARCEL_DELIVERY", "text": "इंडिया पोस्ट: आपका पार्सल गलत पते के कारण अटका हुआ है। 30 रुपये का शुल्क भरें: http://indiapost-redelivery.top"},
    {"lang": "hi", "is_scam": 1, "cat": "JOB_SCAM", "text": "घर बैठे अमेज़न के लिए काम करें और रोजाना 2000-5000 कमाएं। टेलीग्राम जॉइन करें।"},
    {"lang": "hi", "is_scam": 1, "cat": "FAKE_BANK_LINK", "text": "प्रिय पीएनबी ग्राहक, अपने खाते की सुरक्षा के लिए तुरंत नेटबैंकिंग लॉगिन करें: http://pnb-verify.site"},
    {"lang": "hi", "is_scam": 1, "cat": "ELECTRICITY_BILL", "text": "पावर कॉर्पोरेशन: बिल न भरने पर कनेक्शन तुरंत काटा जाएगा। संपर्क 919876543210"},
    {"lang": "hi", "is_scam": 1, "cat": "FAKE_KYC", "text": "केवाईसी पेंडिंग! आपका सिम कार्ड ब्लॉक हो जाएगा। आधार सत्यापन के लिए कॉल करें।"},
    {"lang": "hi", "is_scam": 1, "cat": "UPI_COLLECT_FRAUD", "text": "कलेक्ट रिक्वेस्ट स्वीकार करें और अपने खाते में 3500 रुपये प्राप्त करें।"},
    # 10 Legit
    {"lang": "hi", "is_scam": 0, "cat": "LEGITIMATE", "text": "प्रिय ग्राहक, आपके बैंक खाते XX1234 में 1,500 रुपये जमा हुए हैं। शेष राशि: 6,400 रुपये। - बैंक ऑफ इंडिया"},
    {"lang": "hi", "is_scam": 0, "cat": "LEGITIMATE", "text": "नेटबैंकिंग लॉगिन के लिए आपका ओटीपी 849201 है। यह 3 मिनट तक मान्य है। एसबीआई।"},
    {"lang": "hi", "is_scam": 0, "cat": "LEGITIMATE", "text": "यूपीपीसीएल: आपके बिजली बिल खाता 102938 का 650 रुपये का भुगतान प्राप्त हुआ। धन्यवाद।"},
    {"lang": "hi", "is_scam": 0, "cat": "LEGITIMATE", "text": "अमेज़न: आपका पार्सल आज शाम तक डिलीवर कर दिया जाएगा। ओटीपी: 4921।"},
    {"lang": "hi", "is_scam": 0, "cat": "LEGITIMATE", "text": "एयरटेल: आपका दैनिक 1.5 जीबी डेटा 50% उपयोग हो चुका है। रिचार्ज के लिए थैंक्स ऐप खोलें।"},
    {"lang": "hi", "is_scam": 0, "cat": "LEGITIMATE", "text": "अरे भाई, क्या हम आज शाम को बाजार जा रहे हैं? फोन उठाओ।"},
    {"lang": "hi", "is_scam": 0, "cat": "LEGITIMATE", "text": "अंतिम अनुस्मारक: कृपया अपने विद्यालय की त्रैमासिक फीस 5 नवंबर से पहले जमा करें।"},
    {"lang": "hi", "is_scam": 0, "cat": "LEGITIMATE", "text": "रेलवे आरक्षण: पीएनआर 2481920192 कन्फर्म हो गया है। कोच B3, सीट 24।"},
    {"lang": "hi", "is_scam": 0, "cat": "LEGITIMATE", "text": "डॉक्टर की अपॉइंटमेंट कल सुबह 10:30 बजे मैक्स अस्पताल में तय है।"},
    {"lang": "hi", "is_scam": 0, "cat": "LEGITIMATE", "text": "मां ने कहा है कि आते समय 2 किलो दूध और फल लेते आना।"},

    # ========================== 2. HINGLISH (hi_rom) ==========================
    # 10 Scams
    {"lang": "hi_rom", "is_scam": 1, "cat": "ELECTRICITY_BILL", "text": "Aapka bijli connection aaj raat 9:30 baje kat diya jayega, contact power officer 9812345678"},
    {"lang": "hi_rom", "is_scam": 1, "cat": "FAKE_KYC", "text": "SBI Warning: Aapka account block hone wala hai. Turant KYC update kare http://sbi-kyc.xyz"},
    {"lang": "hi_rom", "is_scam": 1, "cat": "UPI_COLLECT_FRAUD", "text": "GPay cashback Rs 2000 lene ke liye UPI PIN enter kare aur claim kare."},
    {"lang": "hi_rom", "is_scam": 1, "cat": "LOTTERY_PRIZE", "text": "Congratulations aapne KBC me 25 lakh jeete hai WhatsApp kare 9876543210 par."},
    {"lang": "hi_rom", "is_scam": 1, "cat": "PARCEL_DELIVERY", "text": "India Post parcel pending address update. Pay Rs 25 redelivery fee at http://indiapost.top"},
    {"lang": "hi_rom", "is_scam": 1, "cat": "JOB_SCAM", "text": "Part time work from home, earn Rs 3000 daily by liking YouTube videos. Join telegram."},
    {"lang": "hi_rom", "is_scam": 1, "cat": "FAKE_BANK_LINK", "text": "Dear customer your HDFC card is blocked. Reactivate here http://hdfc-card-unblock.site"},
    {"lang": "hi_rom", "is_scam": 1, "cat": "ELECTRICITY_BILL", "text": "Bijli bill baki hai, turant call electricity officer ko karo varna line disconnect hogi."},
    {"lang": "hi_rom", "is_scam": 1, "cat": "FAKE_KYC", "text": "Aapka bank account suspend ho gaya hai. 24 ghante me pan card link kare."},
    {"lang": "hi_rom", "is_scam": 1, "cat": "UPI_COLLECT_FRAUD", "text": "Paise receive karne ke liye collect request accept kare aur UPI PIN dale."},
    # 10 Legit
    {"lang": "hi_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Dear customer, Rs 500 credited to your account XX4921 via UPI. Balance Rs 3,400. SBI"},
    {"lang": "hi_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Your OTP for login is 382910. Valid for 10 minutes. Do not share with anyone. HDFC Bank"},
    {"lang": "hi_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "BSES: Your bill of Rs 890 for Oct is paid successfully. Thank you for using online portal."},
    {"lang": "hi_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Bhai kal sham ko cricket match khelne aana hai ground par 4 baje."},
    {"lang": "hi_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Zomato: Your order from Haldiram is on the way. Delivery partner will reach in 15 mins."},
    {"lang": "hi_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Jio: Your pack is expiring tomorrow. Recharge now on MyJio app to continue service."},
    {"lang": "hi_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Mummy medicine le li hai maine, sham tak ghar aa jaunga."},
    {"lang": "hi_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Uber trip completed. Amount Rs 180 paid via Paytm wallet. Rating 5 stars."},
    {"lang": "hi_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Urgent reminder: Society maintenance bill due date is 5th Nov. Please deposit check."},
    {"lang": "hi_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Happy Diwali to you and your family! Have a wonderful year ahead."},

    # ========================== 3. BENGALI (bn) ==========================
    # 10 Scams
    {"lang": "bn", "is_scam": 1, "cat": "ELECTRICITY_BILL", "text": "বিদ্যুৎ দপ্তর: আপনার বিদ্যুৎ বিল বাকি আছে। আজ রাত ৯ টায় সংযোগ কেটে দেওয়া হবে।"},
    {"lang": "bn", "is_scam": 1, "cat": "FAKE_KYC", "text": "এসবিআই গ্রাহক, আপনার ব্যাংক অ্যাকাউন্ট আজ বন্ধ হয়ে যাবে। কেওয়াইসি আপডেট করুন: http://sbi-kyc.top"},
    {"lang": "bn", "is_scam": 1, "cat": "UPI_COLLECT_FRAUD", "text": "ক্যাশব্যাক ৩০০০ টাকা পেতে ইউপিআই পিন দিন এবং কালেক্ট রিকোয়েস্ট গ্রহণ করুন।"},
    {"lang": "bn", "is_scam": 1, "cat": "LOTTERY_PRIZE", "text": "অভিনন্দন! আপনি কেবিসি লটারিতে ২৫ লাখ টাকা জিতেছেন। অবিলম্বে হোয়াটসঅ্যাপে যোগাযোগ করুন।"},
    {"lang": "bn", "is_scam": 1, "cat": "PARCEL_DELIVERY", "text": "স্পিড পোস্ট: আপনার পার্সেল আটকে গেছে। ২৫ টাকা ফি দিন http://speedpost-update.xyz"},
    {"lang": "bn", "is_scam": 1, "cat": "JOB_SCAM", "text": "ঘরে বসে কাজ করে প্রতিদিন ২০০০ টাকা আয় করুন। টেলিগ্রাম গ্রুপে যুক্ত হন।"},
    {"lang": "bn", "is_scam": 1, "cat": "FAKE_BANK_LINK", "text": "আপনার পিএনবি অ্যাকাউন্ট সাসপেন্ড করা হয়েছে। পুনরায় সক্রিয় করতে লিংকে যান: http://pnb-login.site"},
    {"lang": "bn", "is_scam": 1, "cat": "ELECTRICITY_BILL", "text": "বিদ্যুৎ বিল অবিলম্বে জমা না দিলে লাইন কাটা হবে। বিদ্যুৎ অফিসারের সাথে যোগাযোগ করুন।"},
    {"lang": "bn", "is_scam": 1, "cat": "FAKE_KYC", "text": "প্যান কার্ড লিংক না করলে আপনার ব্যাংক অ্যাকাউন্ট ফ্রিজ হয়ে যাবে।"},
    {"lang": "bn", "is_scam": 1, "cat": "UPI_COLLECT_FRAUD", "text": "টাকা পেতে কিউআর কোড স্ক্যান করুন এবং ইউপিআই পিন এন্টার করুন।"},
    # 10 Legit
    {"lang": "bn", "is_scam": 0, "cat": "LEGITIMATE", "text": "প্রিয় গ্রাহক, আপনার অ্যাকাউন্ট XX4910 এ ৩,০০০ টাকা জমা হয়েছে। অবশিষ্ট ব্যালেন্স: ১২,০০০ টাকা। এসবিআই।"},
    {"lang": "bn", "is_scam": 0, "cat": "LEGITIMATE", "text": "নেটব্যাংকিং ট্রানজ্যাকশনের ওটিপি হল ৮৩৯২০১। এটি ৫ মিনিট পর্যন্ত বৈধ। কাউকে বলবেন না।"},
    {"lang": "bn", "is_scam": 0, "cat": "LEGITIMATE", "text": "ডব্লিউবিএসইডিসিএল: আপনার অক্টোবর মাসের বিদ্যুৎ বিল পরিশোধিত হয়েছে। ধন্যবাদ।"},
    {"lang": "bn", "is_scam": 0, "cat": "LEGITIMATE", "text": "মা, আমি আজ কলেজ শেষ করে বাড়ি ফিরছি। স্টেশনে নেমে ফোন করব।"},
    {"lang": "bn", "is_scam": 0, "cat": "LEGITIMATE", "text": "ফ্লিপকার্ট: আপনার অর্ডার আজ ডেলিভারি হতে চলেছে। ডেলিভারি এজেন্টের নম্বর: ৯৮৩০০১১২৩৪।"},
    {"lang": "bn", "is_scam": 0, "cat": "LEGITIMATE", "text": "জিও: আপনার মাসিক রিচার্জের মেয়াদ ২ দিনে শেষ হবে। মাইজিও অ্যাপ থেকে রিচার্জ করুন।"},
    {"lang": "bn", "is_scam": 0, "cat": "LEGITIMATE", "text": "শুভ বিজয়া! আপনার ও আপনার পরিবারের সকলের জন্য রইল অনেক শুভেচ্ছা।"},
    {"lang": "bn", "is_scam": 0, "cat": "LEGITIMATE", "text": "ডাক্তারবাবুর চেম্বার আজ সন্ধ্যে ৬টায় খোলা থাকবে। আপনার সিরিয়াল নম্বর ৭।"},
    {"lang": "bn", "is_scam": 0, "cat": "LEGITIMATE", "text": "রেলওয়ে কনফার্মেশন: আপনার টিকিট কনফার্ম হয়েছে। বার্থ এস৪/২৮।"},
    {"lang": "bn", "is_scam": 0, "cat": "LEGITIMATE", "text": "জরুরি বিজ্ঞপ্তি: কাল সকালে স্কুলে অভিভাবকদের মিটিং অনুষ্ঠিত হবে।"},

    # ========================== 4. BENGLISH (bn_rom) ==========================
    # 10 Scams
    {"lang": "bn_rom", "is_scam": 1, "cat": "ELECTRICITY_BILL", "text": "Apnar electricity connection aaj ratri 9 tay kete deoya hobe, call korun officer ke."},
    {"lang": "bn_rom", "is_scam": 1, "cat": "FAKE_KYC", "text": "SBI Warning: Apnar bank account block hoye jabe. Ekhuni KYC update korun http://sbi-kyc.xyz"},
    {"lang": "bn_rom", "is_scam": 1, "cat": "UPI_COLLECT_FRAUD", "text": "Taka receive korar jonyo collect request accept korun ebong UPI PIN din."},
    {"lang": "bn_rom", "is_scam": 1, "cat": "LOTTERY_PRIZE", "text": "Apni 25 lakh taka lottery jitechen. Taka pete WhatsApp korun 9830012345."},
    {"lang": "bn_rom", "is_scam": 1, "cat": "PARCEL_DELIVERY", "text": "India Post parcel atke geche. Redelivery fee 25 taka din: http://speedpost.top"},
    {"lang": "bn_rom", "is_scam": 1, "cat": "JOB_SCAM", "text": "Ghore bose part time job kore roj 2000 taka income korun. Telegram join korun."},
    {"lang": "bn_rom", "is_scam": 1, "cat": "FAKE_BANK_LINK", "text": "Apnar account suspend hoyeche. Netbanking login korun http://pnb-update.site"},
    {"lang": "bn_rom", "is_scam": 1, "cat": "ELECTRICITY_BILL", "text": "Bijli bill baki ache, line disconnect hobe aaj ratre. Jogajog korun."},
    {"lang": "bn_rom", "is_scam": 1, "cat": "FAKE_KYC", "text": "24 ghontar modhye pan card link na korle bank account bondho hobe."},
    {"lang": "bn_rom", "is_scam": 1, "cat": "UPI_COLLECT_FRAUD", "text": "PhonePe cashback 4000 taka pete UPI PIN enter korun."},
    # 10 Legit
    {"lang": "bn_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Apnar account XX4810 e 2,000 taka joma hoyeche. Balance 8,500 taka. SBI."},
    {"lang": "bn_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Login OTP holo 492019. Valid for 10 minutes. Share korben na. Axis Bank."},
    {"lang": "bn_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "WBSEDCL: Oct masher electricity bill 750 taka safolbhabe joma hoyeche."},
    {"lang": "bn_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Kire, kal sokale ki college jachhis? Amake ektu phone koris."},
    {"lang": "bn_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Amazon parcel aaj bikele deliver hobe. OTP holo 8291."},
    {"lang": "bn_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Maa ami bazar theke mach ar sobji niye aschi."},
    {"lang": "bn_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Jio pack expire hobe kal. MyJio theke recharge kore nin."},
    {"lang": "bn_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Subho Bijoya! Bhalo theko sobai."},
    {"lang": "bn_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Doctor babur chamber e apnar serial number 5. 6:30 tay asun."},
    {"lang": "bn_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Train ticket confirm hoye geche. Coach S2 berth 34."},

    # ========================== 5. MARATHI (mr) ==========================
    # 10 Scams
    {"lang": "mr", "is_scam": 1, "cat": "ELECTRICITY_BILL", "text": "महावितरण: तुमचे वीज बिल भरले नाही म्हणून आज रात्री वीज पुरवठा खंडित केला जाईल. अधिकारी 9822012345 ला संपर्क करा."},
    {"lang": "mr", "is_scam": 1, "cat": "FAKE_KYC", "text": "प्रिय एसबीआय ग्राहक, तुमचे खाते आज ब्लॉक केले जाईल. केवायसी अपडेट करा: http://sbi-kyc.site"},
    {"lang": "mr", "is_scam": 1, "cat": "UPI_COLLECT_FRAUD", "text": "बक्षीस रक्कम ३००० रुपये मिळवण्यासाठी कलेक्ट रिक्वेस्ट स्वीकारा आणि यूपीआय पिन टाका."},
    {"lang": "mr", "is_scam": 1, "cat": "LOTTERY_PRIZE", "text": "अभिनंदन! तुम्ही लकी ड्रॉ मध्ये १५ लाख जिंकले आहेत. बक्षीस मिळवण्यासाठी संपर्क करा."},
    {"lang": "mr", "is_scam": 1, "cat": "PARCEL_DELIVERY", "text": "स्पीड पोस्ट: तुमचे पार्सल पत्ता चुकीचा असल्यामुळे अडकले आहे. २५ रुपये शुल्क भरा http://indiapost.top"},
    {"lang": "mr", "is_scam": 1, "cat": "JOB_SCAM", "text": "घरी बसून काम करा आणि दररोज २५०० रुपये कमवा. टेलिग्राम ग्रुप जॉइन करा."},
    {"lang": "mr", "is_scam": 1, "cat": "FAKE_BANK_LINK", "text": "तुमचे बँक ऑफ महाराष्ट्र खाते निलंबित झाले आहे. लॉगिन करा: http://bom-verify.site"},
    {"lang": "mr", "is_scam": 1, "cat": "ELECTRICITY_BILL", "text": "वीज बिल न भरल्यास वीज कापली जाईल. त्वरित संपर्क करा."},
    {"lang": "mr", "is_scam": 1, "cat": "FAKE_KYC", "text": "पॅन कार्ड अपडेट न केल्यास बँक खाते २४ तासांत बंद होईल."},
    {"lang": "mr", "is_scam": 1, "cat": "UPI_COLLECT_FRAUD", "text": "पैसे मिळवण्यासाठी यूपीआय पिन टाका."},
    # 10 Legit
    {"lang": "mr", "is_scam": 0, "cat": "LEGITIMATE", "text": "प्रिय ग्राहक, तुमच्या खात्यात रु. ५,००० जमा झाले आहेत. शिल्लक: रु. १८,४००. - बँक ऑफ महाराष्ट्र"},
    {"lang": "mr", "is_scam": 0, "cat": "LEGITIMATE", "text": "नेटबँकिंग ट्रान्झॅक्शनसाठी तुमचा ओटीपी आहे ९४८२०१. कोणालाही सांगू नका. एसबीआय."},
    {"lang": "mr", "is_scam": 0, "cat": "LEGITIMATE", "text": "महावितरण: ऑक्टोबर महिन्याचे वीज बिल रु. ८५० यशस्वीपणे भरले गेले आहे. धन्यवाद."},
    {"lang": "mr", "is_scam": 0, "cat": "LEGITIMATE", "text": "आई, मी आज ऑफिस संपवून संध्याकाळी ७ वाजेपर्यंत घरी पोहोचतो."},
    {"lang": "mr", "is_scam": 0, "cat": "LEGITIMATE", "text": "अमेझॉन: तुमचे पार्सल आज डिलिव्हर केले जाईल. डिलिव्हरी बॉयचा फोन ९८२००१२३४५."},
    {"lang": "mr", "is_scam": 0, "cat": "LEGITIMATE", "text": "जिओ: तुमचा प्लॅन उद्या संपत आहे. सेवा सुरू ठेवण्यासाठी मायजिओ ॲपवरून रिचार्ज करा."},
    {"lang": "mr", "is_scam": 0, "cat": "LEGITIMATE", "text": "दिवाळीच्या तुम्हाला आणि तुमच्या संपूर्ण कुटुंबाला हार्दिक शुभेच्छा!"},
    {"lang": "mr", "is_scam": 0, "cat": "LEGITIMATE", "text": "डॉक्टरांची अपॉइंटमेंट उद्या सकाळी ११ वाजता ठरली आहे."},
    {"lang": "mr", "is_scam": 0, "cat": "LEGITIMATE", "text": "रेल्वे आरक्षण: तिकीट कन्फर्म झाले आहे. बोगी बी२, बर्थ क्रमांक ४२."},
    {"lang": "mr", "is_scam": 0, "cat": "LEGITIMATE", "text": "सोसायटी मेंटेनन्स बिल भरण्याची अंतिम तारीख ५ नोव्हेंबर आहे."},

    # ========================== 6. MARATHI ROMANIZED (mr_rom) ==========================
    # 10 Scams
    {"lang": "mr_rom", "is_scam": 1, "cat": "ELECTRICITY_BILL", "text": "Aapla bijli connection aaj ratri kapla jail, call electricity officer 9822012345."},
    {"lang": "mr_rom", "is_scam": 1, "cat": "FAKE_KYC", "text": "Aaple SBI account block honar aahe, 24 tasat KYC purna kara http://sbi-kyc.site"},
    {"lang": "mr_rom", "is_scam": 1, "cat": "UPI_COLLECT_FRAUD", "text": "Paise milnyasathi collect request accept kara aani UPI PIN taka."},
    {"lang": "mr_rom", "is_scam": 1, "cat": "LOTTERY_PRIZE", "text": "Abhinandan! Tumhi 15 lakh lottery jinkli aahe. Sampark kara WhatsApp var."},
    {"lang": "mr_rom", "is_scam": 1, "cat": "PARCEL_DELIVERY", "text": "Speed post parcel atkle aahe. Address update kara http://indiapost-update.top"},
    {"lang": "mr_rom", "is_scam": 1, "cat": "JOB_SCAM", "text": "Ghari basun part time kaam kara roj 2000 kamva. Telegram group join kara."},
    {"lang": "mr_rom", "is_scam": 1, "cat": "FAKE_BANK_LINK", "text": "Bank account suspend zale aahe. Netbanking login kara http://bom-verify.site"},
    {"lang": "mr_rom", "is_scam": 1, "cat": "ELECTRICITY_BILL", "text": "Mahavitaran bill baki aahe, vij purvatha khandit honar aaj ratri."},
    {"lang": "mr_rom", "is_scam": 1, "cat": "FAKE_KYC", "text": "Pan card link kara nahi tar account freeze honar aahe."},
    {"lang": "mr_rom", "is_scam": 1, "cat": "UPI_COLLECT_FRAUD", "text": "Cashback reward 4000 sathi UPI PIN taka aani claim kara."},
    # 10 Legit
    {"lang": "mr_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Khate XX3921 madhe Rs 3,000 credit zale aahe. Balance Rs 14,000. Bank of Maharashtra."},
    {"lang": "mr_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Netbanking transaction sathi OTP aahe 849201. Konalahi sangu naka. SBI."},
    {"lang": "mr_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Mahavitaran: Bill Rs 850 successfully bharle gele aahe. Dhanyawad."},
    {"lang": "mr_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Aai me aaj sandhyakali 7 waje paryant ghari yeto."},
    {"lang": "mr_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Amazon parcel aaj deliver honar aahe. Delivery code 3921."},
    {"lang": "mr_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Jio pack expire honar udya. MyJio app varun recharge kara."},
    {"lang": "mr_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Diwalichya hardik shubheccha tumhala aani tumchya kutumbala!"},
    {"lang": "mr_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Doctoranchi appointment udya sakali 11 wajta aahe."},
    {"lang": "mr_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Railway booking confirm zali aahe. Seat S3 45."},
    {"lang": "mr_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Bhai kal cricket khelayla ground var 4 wajta ye."},

    # ========================== 7. KANNADA (kn) ==========================
    # 10 Scams
    {"lang": "kn", "is_scam": 1, "cat": "ELECTRICITY_BILL", "text": "ಬೆಸ್ಕಾಂ: ನಿಮ್ಮ ವಿದ್ಯುತ್ ಬಿಲ್ ಬಾಕಿ ಇದೆ. ಇಂದು ರಾತ್ರಿ 9:30 ಕ್ಕೆ ಸಂಪರ್ಕ ಕಡಿತಗೊಳಿಸಲಾಗುವುದು. ಸಂಪರ್ಕಿಸಿ: 9845012345"},
    {"lang": "kn", "is_scam": 1, "cat": "FAKE_KYC", "text": "ನಿಮ್ಮ ಬ್ಯಾಂಕ್ ಖಾತೆಯನ್ನು ನಿರ್ಬಂಧಿಸಲಾಗಿದೆ. ತಕ್ಷಣ ಕೆವೈಸಿ ಅಪ್‌ಡೇಟ್ ಮಾಡಲು ಇಲ್ಲಿ ಕ್ಲಿಕ್ ಮಾಡಿ: http://sbi-kyc.top"},
    {"lang": "kn", "is_scam": 1, "cat": "UPI_COLLECT_FRAUD", "text": "ಕ್ಯಾಶ್‌ಬ್ಯಾಕ್ 4000 ಪಡೆಯಲು ಕಲೆಕ್ಟ್ ರಿಕ್ವೆಸ್ಟ್ ಒಪ್ಪಿಕೊಳ್ಳಿ ಮತ್ತು ಯುಪಿಐ ಪಿನ್ ಹಾಕಿ."},
    {"lang": "kn", "is_scam": 1, "cat": "LOTTERY_PRIZE", "text": "ಅಭಿನಂದನೆಗಳು! ನೀವು 25 ಲಕ್ಷ ಲಾಟರಿ ಗೆದ್ದಿದ್ದೀರಿ. ಹಣ ಪಡೆಯಲು ವಾಟ್ಸಾಪ್ ಸಂಪರ್ಕಿಸಿ."},
    {"lang": "kn", "is_scam": 1, "cat": "PARCEL_DELIVERY", "text": "ಇಂಡಿಯಾ ಪೋಸ್ಟ್: ನಿಮ್ಮ ಪಾರ್ಸೆಲ್ ವಿತರಣೆ ವಿಫಲವಾಗಿದೆ. ರೂ 25 ಶುಲ್ಕ ಪಾವತಿಸಿ: http://indiapost.top"},
    {"lang": "kn", "is_scam": 1, "cat": "JOB_SCAM", "text": "ಮನೆಯಿಂದಲೇ ಕೆಲಸ ಮಾಡಿ ದಿನಕ್ಕೆ 2000 ಗಳಿಸಿ. ಟೆಲಿಗ್ರಾಂ ಲಿಂಕ್ ಸಂಪರ್ಕಿಸಿ."},
    {"lang": "kn", "is_scam": 1, "cat": "FAKE_BANK_LINK", "text": "ನಿಮ್ಮ ಕೆನರಾ ಬ್ಯಾಂಕ್ ಖಾತೆ ಅಮಾನತುಗೊಂಡಿದೆ. ಲಾಗಿನ್ ಮಾಡಿ: http://canara-login.site"},
    {"lang": "kn", "is_scam": 1, "cat": "ELECTRICITY_BILL", "text": "ವಿದ್ಯುತ್ ಬಿಲ್ ಪಾವತಿಸದಿದ್ದರೆ ತಕ್ಷಣ ವಿದ್ಯುತ್ ಸಂಪರ್ಕ ಕಡಿತ. ಕರೆ ಮಾಡಿ."},
    {"lang": "kn", "is_scam": 1, "cat": "FAKE_KYC", "text": "ಪ್ಯಾನ್ ಕಾರ್ಡ್ ಲಿಂಕ್ ಮಾಡದಿದ್ದರೆ ಖಾತೆ ಶಾಶ್ವತವಾಗಿ ಮುಚ್ಚಲಾಗುತ್ತದೆ."},
    {"lang": "kn", "is_scam": 1, "cat": "UPI_COLLECT_FRAUD", "text": "ಹಣ ಪಡೆಯಲು ಯುಪಿಐ ಪಿನ್ ನಮೂದಿಸಿ."},
    # 10 Legit
    {"lang": "kn", "is_scam": 0, "cat": "LEGITIMATE", "text": "ಗ್ರಾಹಕರೇ, ನಿಮ್ಮ ಖಾತೆಗೆ ರೂ. ೪,೦೦೦ ಜಮೆಯಾಗಿದೆ. ಲಭ್ಯವಿರುವ ಬ್ಯಾಲೆನ್ಸ್: ರೂ. ೧೨,೮೦೦. - ಕೆನರಾ ಬ್ಯಾಂಕ್"},
    {"lang": "kn", "is_scam": 0, "cat": "LEGITIMATE", "text": "ಲಾಗಿನ್ ಒಟಿಪಿ ೮೪೯೨೦೧. ೧೦ ನಿಮಿಷಗಳವರೆಗೆ ಮಾನ್ಯವಾಗಿದೆ. ಯಾರೊಂದಿಗೂ ಹಂಚಿಕೊಳ್ಳಬೇಡಿ. ಎಸ್ಬಿಐ."},
    {"lang": "kn", "is_scam": 0, "cat": "LEGITIMATE", "text": "ಬೆಸ್ಕಾಂ: ನಿಮ್ಮ ಅಕ್ಟೋಬರ್ ತಿಂಗಳ ವಿದ್ಯುತ್ ಬಿಲ್ ರೂ ೬೫೦ ಯಶಸ್ವಿಯಾಗಿ ಪಾವತಿಯಾಗಿದೆ. ಧನ್ಯವಾದಗಳು."},
    {"lang": "kn", "is_scam": 0, "cat": "LEGITIMATE", "text": "ಅಮ್ಮ, ನಾನು ಕಾಲೇಜು ಮುಗಿಸಿ ಸಂಜೆ ೬ ಗಂಟೆಗೆ ಮನೆಗೆ ಬರುತ್ತೇನೆ."},
    {"lang": "kn", "is_scam": 0, "cat": "LEGITIMATE", "text": "ಅಮೆಜಾನ್: ನಿಮ್ಮ ಆರ್ಡರ್ ಇಂದು ವಿತರಣೆಯಾಗಲಿದೆ. ವಿತರಣಾ ಏಜೆಂಟ್: ೯೮೪೫೦೧೨೩೪೫."},
    {"lang": "kn", "is_scam": 0, "cat": "LEGITIMATE", "text": "ಜಿಯೋ: ನಿಮ್ಮ ಪ್ಯಾಕ್ ನಾಳೆ ಮುಕ್ತಾಯಗೊಳ್ಳಲಿದೆ. ಮೈಜಿಯೋ ಆ್ಯಪ್ ಮೂಲಕ ರೀಚಾರ್ಜ್ ಮಾಡಿ."},
    {"lang": "kn", "is_scam": 0, "cat": "LEGITIMATE", "text": "ದೀಪಾವಳಿ ಹಬ್ಬದ ಹಾರ್ದಿಕ ಶುಭಾಶಯಗಳು!"},
    {"lang": "kn", "is_scam": 0, "cat": "LEGITIMATE", "text": "ವೈದ್ಯರ ಅಪಾಯಿಂಟ್‌ಮೆಂಟ್ ನಾಳೆ ಬೆಳಿಗ್ಗೆ ೧೦:೩೦ ಕ್ಕೆ ನಿಗದಿಯಾಗಿದೆ."},
    {"lang": "kn", "is_scam": 0, "cat": "LEGITIMATE", "text": "ರೈಲು ಬುಕಿಂಗ್ ಖಚಿತವಾಗಿದೆ. ಬೋಗಿ ಎಸ್೩, ಬರ್ತ್ ೩೨."},
    {"lang": "kn", "is_scam": 0, "cat": "LEGITIMATE", "text": "ಸೊಸೈಟಿ ನಿರ್ವಹಣಾ ಶುಲ್ಕ ಪಾವತಿಸಲು ಕೊನೆಯ ದಿನಾಂಕ ನವೆಂಬರ್ ೫."},

    # ========================== 8. KANNADA ROMANIZED (kn_rom) ==========================
    # 10 Scams
    {"lang": "kn_rom", "is_scam": 1, "cat": "ELECTRICITY_BILL", "text": "Vidyuth bill baki ide, eevathu night connection cut aaguthe. Call electricity officer 9845012345."},
    {"lang": "kn_rom", "is_scam": 1, "cat": "FAKE_KYC", "text": "Nimma bank account block aagide. Eegale KYC update maadi http://sbi-kyc.site"},
    {"lang": "kn_rom", "is_scam": 1, "cat": "UPI_COLLECT_FRAUD", "text": "Hana padeyalu collect request accept maadi UPI PIN haaki."},
    {"lang": "kn_rom", "is_scam": 1, "cat": "LOTTERY_PRIZE", "text": "Abhinandanegalu! Neevu 25 lakh lottery geddiddiri. WhatsApp samparkisi."},
    {"lang": "kn_rom", "is_scam": 1, "cat": "PARCEL_DELIVERY", "text": "India post parcel hold aagide. Rs 25 fee pay maadi http://speedpost.top"},
    {"lang": "kn_rom", "is_scam": 1, "cat": "JOB_SCAM", "text": "Mane kelsa maadi dina 2000 earn maadi. Telegram group join aagi."},
    {"lang": "kn_rom", "is_scam": 1, "cat": "FAKE_BANK_LINK", "text": "Bank account suspend aagide. Login maadi http://canara-login.site"},
    {"lang": "kn_rom", "is_scam": 1, "cat": "ELECTRICITY_BILL", "text": "Bescom bill baki ide, line disconnect aaguthe eevathu."},
    {"lang": "kn_rom", "is_scam": 1, "cat": "FAKE_KYC", "text": "Pan card link maadade idre account freeze aaguthe 24 hours nalli."},
    {"lang": "kn_rom", "is_scam": 1, "cat": "UPI_COLLECT_FRAUD", "text": "Cashback reward 4000 pete UPI PIN enter maadi."},
    # 10 Legit
    {"lang": "kn_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Nimma account XX2910 ge Rs 3,000 credit aagide. Balance Rs 14,000. Canara Bank."},
    {"lang": "kn_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Login OTP 382910. Valid for 10 minutes. Share maadbedi. SBI."},
    {"lang": "kn_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Bescom bill Rs 750 successfully pay aagide. Dhanyavadagalu."},
    {"lang": "kn_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Amma naanu sanje 6 gantege manege barthini."},
    {"lang": "kn_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Amazon parcel ivathu deliver aaguthe. Delivery boy 9845012345."},
    {"lang": "kn_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Jio pack expire aaguthe naale. MyJio inda recharge maadi."},
    {"lang": "kn_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Deepavali habbada shubhashayagalu nimma kutumbakke!"},
    {"lang": "kn_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Doctor appointment naale beligge 10:30 ge ide."},
    {"lang": "kn_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Train ticket confirm aagide. Seat S2 24."},
    {"lang": "kn_rom", "is_scam": 0, "cat": "LEGITIMATE", "text": "Macha naale cricket match ground ge 4 gantege baa."},

    # ========================== 9. ENGLISH (en) ==========================
    # 10 Scams
    {"lang": "en", "is_scam": 1, "cat": "ELECTRICITY_BILL", "text": "Electricity dept: Your power connection will be disconnected tonight at 9:30 PM due to unpaid bill. Call officer 9876543210."},
    {"lang": "en", "is_scam": 1, "cat": "FAKE_KYC", "text": "Dear SBI Customer, your bank account is suspended. Update your KYC immediately at http://sbi-kyc-verify.xyz"},
    {"lang": "en", "is_scam": 1, "cat": "UPI_COLLECT_FRAUD", "text": "GooglePay: You have won Rs 5,000 cash reward. Accept collect request and enter UPI PIN to receive money."},
    {"lang": "en", "is_scam": 1, "cat": "LOTTERY_PRIZE", "text": "Congratulations! Your mobile number won 25 Lakhs in KBC Lucky Draw. Contact WhatsApp manager at 919876543210."},
    {"lang": "en", "is_scam": 1, "cat": "PARCEL_DELIVERY", "text": "India Post: Your package could not be delivered due to wrong address. Pay Rs 25 redelivery fee at http://indiapost-parcel.top"},
    {"lang": "en", "is_scam": 1, "cat": "JOB_SCAM", "text": "Work from home part time job! Earn Rs 3,000 to 8,000 daily by rating hotels. Join Telegram channel @workfromhome2026"},
    {"lang": "en", "is_scam": 1, "cat": "FAKE_BANK_LINK", "text": "HDFC Alert: Your NetBanking is deactivated. Reactivate your access by clicking http://hdfcbank-netbanking-portal.site"},
    {"lang": "en", "is_scam": 1, "cat": "ELECTRICITY_BILL", "text": "Urgent notice: Power cutoff scheduled tonight. Contact electricity officer immediately to clear dues."},
    {"lang": "en", "is_scam": 1, "cat": "FAKE_KYC", "text": "Your account will be blocked within 24 hours. Update PAN details now to continue debit card transactions."},
    {"lang": "en", "is_scam": 1, "cat": "UPI_COLLECT_FRAUD", "text": "Scan this QR code and enter UPI PIN to claim your Rs 2,500 refund into your bank account."},
    # 10 Legit
    {"lang": "en", "is_scam": 0, "cat": "LEGITIMATE", "text": "Dear Customer, your A/C XX4921 has been credited with Rs 5,000.00 on 30-Oct-26 via UPI ref 492104829102. Avl Bal: Rs 24,500.00. SBI"},
    {"lang": "en", "is_scam": 0, "cat": "LEGITIMATE", "text": "849201 is the OTP for transaction of Rs 1,299.00 on HDFC Bank Card ending 4019. Valid for 10 mins. Never share OTP with anyone."},
    {"lang": "en", "is_scam": 0, "cat": "LEGITIMATE", "text": "BSES Rajdhani: Payment of Rs 1,450.00 for CA 100294819 received with thanks on 30-Oct-2026. Official website https://www.bsesdelhi.com"},
    {"lang": "en", "is_scam": 0, "cat": "LEGITIMATE", "text": "Amazon: Your package 402-8392018 is out for delivery today with delivery partner Rajesh. Share delivery OTP 3921."},
    {"lang": "en", "is_scam": 0, "cat": "LEGITIMATE", "text": "Airtel: Your recharge of Rs 299 is expiring in 2 days. Recharge today on Airtel Thanks App to continue unlimited 5G data."},
    {"lang": "en", "is_scam": 0, "cat": "LEGITIMATE", "text": "Hey Mom, I just landed in Delhi airport. Will take a cab and reach home by 9 PM."},
    {"lang": "en", "is_scam": 0, "cat": "LEGITIMATE", "text": "Doctor appointment scheduled for tomorrow at 11:00 AM with Dr. Sharma at Apollo Hospital."},
    {"lang": "en", "is_scam": 0, "cat": "LEGITIMATE", "text": "Indian Railways: PNR 2481920192 is confirmed. Coach B3, Berth 24. Train departs at 06:15 AM from New Delhi."},
    {"lang": "en", "is_scam": 0, "cat": "LEGITIMATE", "text": "URGENT REMINDER: Annual property tax payment due date is 15th Nov. Please deposit online at official civic portal."},
    {"lang": "en", "is_scam": 0, "cat": "LEGITIMATE", "text": "Swiggy: Your order from Burger King has been delivered. Enjoy your meal and please rate your experience!"}
]

def run_ml_benchmark():
    print(f"=== Section 8: ML Honesty Benchmark on {len(HELD_OUT_DATA)} Held-Out Samples ===")
    
    by_lang = defaultdict(lambda: {"tp": 0, "fp": 0, "tn": 0, "fn": 0, "missed_scams": [], "false_positives": []})
    
    total_tp = total_fp = total_tn = total_fn = 0
    
    for item in HELD_OUT_DATA:
        lang = item["lang"]
        text = item["text"]
        actual_is_scam = item["is_scam"]
        inp = "url" if text.startswith("http") or text.startswith("upi:") else "text"
        
        # Strip script code suffix for api language parameter
        base_lang = lang.split("_")[0]
        
        res = detector.analyze(input_type=inp, content=text, language=base_lang)
        pred_is_scam = 1 if res["risk_score"] >= 0.30 else 0
        
        if actual_is_scam == 1:
            if pred_is_scam == 1:
                by_lang[lang]["tp"] += 1
                total_tp += 1
            else:
                by_lang[lang]["fn"] += 1
                total_fn += 1
                by_lang[lang]["missed_scams"].append((item["cat"], text, res["risk_score"], res["category"]))
        else:
            if pred_is_scam == 1:
                by_lang[lang]["fp"] += 1
                total_fp += 1
                by_lang[lang]["false_positives"].append((item["cat"], text, res["risk_score"], res["category"], res["reason_codes"]))
            else:
                by_lang[lang]["tn"] += 1
                total_tn += 1

    overall_p = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    overall_r = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    overall_f1 = (2 * overall_p * overall_r) / (overall_p + overall_r) if (overall_p + overall_r) > 0 else 0.0
    overall_fpr = total_fp / (total_fp + total_tn) if (total_fp + total_tn) > 0 else 0.0
    overall_acc = (total_tp + total_tn) / len(HELD_OUT_DATA)

    print("\n" + "=" * 80)
    print("                REAL HELD-OUT PERFORMANCE BENCHMARK (180 SAMPLES)         ")
    print("=" * 80)
    print(f"Overall Accuracy:                 {overall_acc * 100:.2f}%  (Claimed: 92.11%)")
    print(f"Overall Precision:                {overall_p * 100:.2f}%  (Claimed: 100.00%)")
    print(f"Overall Recall:                   {overall_r * 100:.2f}%  (Claimed: 89.09%)")
    print(f"Overall F1 Score:                 {overall_f1 * 100:.2f}%  (Claimed: 94.23%)")
    print(f"Overall False Positive Rate (FPR): {overall_fpr * 100:.2f}%  (Claimed: 0.00%)")
    print(f"Total True Positives:             {total_tp} / 90 scams")
    print(f"Total True Negatives:             {total_tn} / 90 legit")
    print(f"Total False Positives:            {total_fp}")
    print(f"Total False Negatives (Missed):   {total_fn}")

    print("\n" + "-" * 80)
    print(f"{'Language / Script':<16} | {'Samples':<8} | {'Precision':<10} | {'Recall':<10} | {'F1 Score':<10} | {'FPR':<8}")
    print("-" * 80)

    # Claimed in MODEL_CARD.md
    claimed = {
        "bn": {"p": 100.0, "r": 100.0, "f1": 100.0},
        "bn_rom": {"p": 100.0, "r": 50.0, "f1": 66.7},
        "en": {"p": 100.0, "r": 100.0, "f1": 100.0},
        "hi": {"p": 100.0, "r": 100.0, "f1": 100.0},
        "hi_rom": {"p": 100.0, "r": 71.4, "f1": 83.3},
        "kn": {"p": 100.0, "r": 100.0, "f1": 100.0},
        "kn_rom": {"p": 100.0, "r": 66.7, "f1": 80.0},
        "mr": {"p": 100.0, "r": 83.3, "f1": 90.9},
        "mr_rom": {"p": 100.0, "r": 66.7, "f1": 80.0},
    }

    for lang in sorted(by_lang.keys()):
        c = by_lang[lang]
        tp = c["tp"]
        fp = c["fp"]
        tn = c["tn"]
        fn = c["fn"]
        p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * p * r) / (p + r) if (p + r) > 0 else 0.0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        cl = claimed.get(lang, {})
        print(f"{lang:<16} | 10S + 10L| {p*100:>8.1f}% | {r*100:>8.1f}% | {f1*100:>8.1f}% | {fpr*100:>6.1f}%")

    print("\n" + "=" * 80)
    print("                 DETAILED ANALYSIS OF MISSED SCAMS                  ")
    print("=" * 80)
    for lang in sorted(by_lang.keys()):
        c = by_lang[lang]
        if c["missed_scams"]:
            print(f"\n[Language: {lang}] Missed {len(c['missed_scams'])} scams:")
            for ms in c["missed_scams"]:
                print(f"  - Cat: {ms[0]:<18} | Score: {ms[2]} | Classified as: {ms[3]}")
                print(f"    Text: {ms[1]}")

    if total_fp > 0:
        print("\n" + "=" * 80)
        print("                 DETAILED ANALYSIS OF FALSE POSITIVES               ")
        print("=" * 80)
        for lang in sorted(by_lang.keys()):
            c = by_lang[lang]
            if c["false_positives"]:
                print(f"\n[Language: {lang}] False positives: {len(c['false_positives'])}")
                for fp_item in c["false_positives"]:
                    print(f"  - Text: {fp_item[1]}")
                    print(f"    Score: {fp_item[2]} | Cat: {fp_item[3]} | Reasons: {fp_item[4]}")

if __name__ == "__main__":
    run_ml_benchmark()
