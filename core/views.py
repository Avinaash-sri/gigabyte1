import random
import time
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import SignUpForm
from .models import ScanLog

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def dashboard_view(request):
    logs = ScanLog.objects.filter(user=request.user).order_by('-scanned_at')[:5]
    return render(request, 'dashboard.html', {'logs': logs})

import requests
import re

@login_required
def verify_url_api(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        print(f"Received verification request for: {url}")
        
        if not url:
            return JsonResponse({'error': 'No URL provided'}, status=400)
            
        # Ensure URL schema
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        # --- 1. Real Connectivity Check (API) ---
        connectivity_score = 0
        try:
            # Short timeout to prevent hanging
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                connectivity_score = 100
            else:
                connectivity_score = 40 # Up but issue
        except requests.exceptions.RequestException:
            connectivity_score = 0 # Down or unreachable

        # --- 2. Heuristic "AI" Analysis ---
        
        # A. Trusted Domain Whitelist (Simulated Knowledge Base)
        trusted_domains = ['linkedin.com', 'indeed.com', 'glassdoor.com', 'google.com', 'naukri.com', 'monster.com', 'upwork.com', 'fiverr.com']
        is_trusted = any(domain in url.lower() for domain in trusted_domains)
        
        # B. Suspicious Pattern Detection
        suspicious_keywords = ['scam', 'fake', 'risk', 'free', 'money', 'crypto', 'login', 'account', 'verify', 'bank', 'secure', 'alert']
        found_keywords = [word for word in suspicious_keywords if word in url.lower()]
        has_suspicious_patterns = len(found_keywords) > 0
        
        # C. TLD Check
        suspicious_tlds = ['.xyz', '.top', '.club', '.info', '.gq', '.cf']
        has_suspicious_tld = any(url.lower().endswith(tld) for tld in suspicious_tlds)

        # --- 3. Scoring Engine ---
        
        # Legitimacy: Based on connectivity and trusted domain status
        if is_trusted:
            legitimacy_score = 95
        elif connectivity_score == 0:
            legitimacy_score = 10
        else:
            legitimacy_score = 60 # Unknown but accessible

        # Brand: High if trusted, medium-low otherwise
        brand_score = 90 if is_trusted else 40

        # Scam Pattern: (Lower is Better/Safer, High is Bad)
        # Base score
        scam_score = 10 
        if has_suspicious_patterns:
            scam_score += 50
        if has_suspicious_tld:
            scam_score += 30
        if not is_trusted and len(url) > 50: # Long URLs are often tracking/scam
            scam_score += 10
        
        # Cap scam score
        scam_score = min(scam_score, 100)

        # Reviews: Simulated
        if is_trusted:
            review_score = random.randint(85, 98)
        elif scam_score > 50:
            review_score = random.randint(10, 30)
        else:
            review_score = random.randint(40, 70)

        # --- 4. Final Calculation ---
        # Formula: High Legitimacy + High Brand - High Scam + High Review
        
        # Invert scam for trust calculation (100 - scam)
        trust_components = [
            legitimacy_score * 0.3,
            brand_score * 0.2,
            (100 - scam_score) * 0.3,
            review_score * 0.2
        ]
        
        final_score = int(sum(trust_components))
        
        # HARD OVERRIDES
        if scam_score > 80:
             final_score = min(final_score, 20) # Force fail if highly suspicious
        
        risk_score = 100 - final_score
        is_safe = final_score >= 70

        # Log
        try:
            ScanLog.objects.create(user=request.user, url=url, risk_score=risk_score, is_safe=is_safe)
        except Exception as e:
            print(f"Error saving log: {e}")

        return JsonResponse({
            'url': url,
            'trust_score': final_score,
            'risk_score': risk_score,
            'is_safe': is_safe,
            'breakdown': {
                'legitimacy': legitimacy_score,
                'brand': brand_score,
                'scam': scam_score,
                'reviews': review_score
            },
            'message': 'Verification Complete'
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)
