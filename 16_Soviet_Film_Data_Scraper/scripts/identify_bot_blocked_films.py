"""
Identify all films that have bot detection/CAPTCHA messages in their summaries.
These are summaries that contain bot blocking text instead of actual film descriptions.
"""
import csv
import sys
import re

def is_bot_blocked_summary(summary):
    """Check if summary contains bot detection/CAPTCHA messages."""
    if not summary or len(summary.strip()) < 50:
        return False, None
    
    summary_lower = summary.lower()
    
    # Bot detection patterns
    bot_patterns = [
        ('please confirm', 'Please confirm that you are not a robot'),
        ('you are not a robot', 'CAPTCHA verification message'),
        ('automated requests', 'Automated request detected'),
        ('we\'re sorry, but it looks like requests', 'Cloudflare/CAPTCHA blocking'),
        ('after checkbox', 'CAPTCHA checkbox message'),
        ('bot detected', 'Bot detection message'),
        ('access denied', 'Access denied message'),
        ('captcha', 'CAPTCHA page'),
        ('verify you are human', 'Human verification'),
        ('blocked', 'Blocked by security'),
        ('rate limit', 'Rate limiting message'),
        ('too many requests', 'Too many requests message'),
        ('cloudflare', 'Cloudflare protection'),
        ('checking your browser', 'Browser verification'),
        ('javascript required', 'JavaScript requirement'),
    ]
    
    for pattern, description in bot_patterns:
        if pattern in summary_lower[:1000]:  # Check first 1000 chars
            # Additional check: if it's short and has bot keywords, definitely a bot message
            if len(summary) < 500 or (len(summary) < 800 and summary_lower.count(pattern) > 0):
                return True, description
    
    # Check for combination of bot keywords (more reliable)
    bot_keywords = [
        'please confirm', 'you are not a robot', 'automated requests',
        'we\'re sorry, but it looks like requests', 'after checkbox',
        'bot detected', 'captcha', 'verify you are human'
    ]
    keyword_count = sum(1 for keyword in bot_keywords if keyword in summary_lower[:800])
    if keyword_count >= 2:  # If 2+ bot keywords present
        return True, f'Multiple bot detection patterns ({keyword_count} found)'
    
    return False, None

def identify_bot_blocked_films(csv_file, output_csv):
    """Scan CSV and identify all films with bot blocking issues."""
    rows = []
    bot_blocked = []
    
    print(f"Reading {csv_file}...")
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        for i, row in enumerate(reader):
            rows.append(row)
            summary = row.get('web_summary', '').strip()
            
            if summary:
                is_bot, reason = is_bot_blocked_summary(summary)
                if is_bot:
                    bot_blocked.append({
                        'index': i + 1,
                        'name_russian': row.get('name_russian', ''),
                        'name_original': row.get('name_original', ''),
                        'year': row.get('production_year', '') or row.get('soviet_release_year', ''),
                        'bot_message_type': reason,
                        'summary_preview': summary[:300] + '...' if len(summary) > 300 else summary
                    })
    
    print(f"\n{'='*70}")
    print(f"BOT BLOCKING DETECTION REPORT")
    print(f"{'='*70}")
    print(f"\nTotal films scanned: {len(rows)}")
    print(f"Films with bot blocking: {len(bot_blocked)}")
    print(f"Percentage: {len(bot_blocked)*100/len(rows):.1f}%")
    
    if bot_blocked:
        print(f"\n{'='*70}")
        print(f"DETAILED LIST OF BOT-BLOCKED FILMS")
        print(f"{'='*70}\n")
        
        for film in bot_blocked[:50]:  # Show first 50
            print(f"Film #{film['index']}: {film['name_russian']} ({film['year']})")
            print(f"  Issue: {film['bot_message_type']}")
            print(f"  Preview: {film['summary_preview'][:150]}...")
            print()
        
        if len(bot_blocked) > 50:
            print(f"... and {len(bot_blocked) - 50} more films with bot blocking")
    
    # Save to CSV
    print(f"\n{'='*70}")
    print(f"Saving results to {output_csv}...")
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['index', 'name_russian', 'name_original', 'year', 'bot_message_type', 'summary_preview'])
        writer.writeheader()
        writer.writerows(bot_blocked)
    
    print(f"✓ Saved {len(bot_blocked)} bot-blocked films to {output_csv}")
    
    return bot_blocked

if __name__ == "__main__":
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "soviet_releases_1950_1991_with_summaries.csv"
    output_csv = sys.argv[2] if len(sys.argv) > 2 else "soviet_releases_1950_1991_with_summaries_BOT_BLOCKED.csv"
    
    identify_bot_blocked_films(csv_file, output_csv)


