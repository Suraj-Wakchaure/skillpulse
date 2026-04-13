"""
Skill Normalization Module
Combines rule-based normalization with automatic similarity detection
"""

from difflib import SequenceMatcher

# Small manual dictionary for common variations
MANUAL_MAPPINGS = {
    'git': 'Git',
    'react.js': 'React',
    'vue.js': 'Vue',
    'node.js': 'Node.js',
    'express.js': 'Express',
    'js': 'JavaScript',
    'ts': 'TypeScript',
    'k8s': 'Kubernetes',
    'ml': 'Machine Learning',
    'ai': 'AI',
    'mongo': 'MongoDB',
    'postgres': 'PostgreSQL',
    'gcp': 'GCP',
    'aws': 'AWS',
    'python3': 'Python',
    'php7': 'PHP',
    'php8': 'PHP',
    'html5': 'HTML',
    'css3': 'CSS',
}

UPPERCASE_SKILLS = ['html', 'css', 'php', 'sql', 'api', 'rest', 'aws', 'gcp', 'ios', 'xml', 'json']


def normalize_skill(skill_name):
    """Rule-based normalization"""
    if not skill_name or not isinstance(skill_name, str):
        return skill_name
    
    cleaned = skill_name.strip()
    if not cleaned:
        return None
    
    lowercase = cleaned.lower()
    
    # Check manual mappings
    if lowercase in MANUAL_MAPPINGS:
        return MANUAL_MAPPINGS[lowercase]
    
    # Remove suffixes
    cleaned = cleaned.replace('.js', '').replace('-', ' ').strip()
    
    # Apply formatting
    words = cleaned.split()
    normalized_words = []
    
    for word in words:
        word_lower = word.lower()
        
        if word_lower in UPPERCASE_SKILLS:
            normalized_words.append(word.upper() if len(word) <= 4 else word.capitalize())
        elif any(c.isupper() for c in word[1:]):
            normalized_words.append(word)
        else:
            normalized_words.append(word.capitalize())
    
    return ' '.join(normalized_words)


def normalize_skill_list(skills):
    """Normalize list and remove duplicates"""
    if not skills:
        return []
    
    normalized = set()
    for skill in skills:
        if skill:
            norm = normalize_skill(skill)
            if norm:
                normalized.add(norm)
    
    return sorted(list(normalized))


def find_similar_skills(skill_list, threshold=0.85):
    """
    Automatically detect similar skills using string similarity
    
    Args:
        skill_list: List of unique skill names
        threshold: Similarity threshold (0.85 = 85% similar)
    
    Returns:
        List of groups, each group contains similar skills
    """
    groups = []
    processed = set()
    
    for i, skill1 in enumerate(skill_list):
        if skill1 in processed:
            continue
        
        group = [skill1]
        
        for skill2 in skill_list[i+1:]:
            if skill2 in processed:
                continue
            
            # Calculate similarity
            similarity = SequenceMatcher(None, skill1.lower(), skill2.lower()).ratio()
            
            if similarity >= threshold:
                group.append(skill2)
                processed.add(skill2)
        
        if len(group) > 1:
            groups.append(group)
        
        processed.add(skill1)
    
    return groups

# Skill category mappings
SKILL_CATEGORIES = {
    # Frontend
    'React': 'Frontend',
    'Angular': 'Frontend',
    'Vue': 'Frontend',
    'HTML': 'Frontend',
    'CSS': 'Frontend',
    'JavaScript': 'Frontend',
    'TypeScript': 'Frontend',
    'Webpack': 'Frontend',
    'Babel': 'Frontend',
    'SASS': 'Frontend',
    
    # Backend
    'Node.js': 'Backend',
    'Express': 'Backend',
    'Django': 'Backend',
    'Flask': 'Backend',
    'FastAPI': 'Backend',
    'PHP': 'Backend',
    'Python': 'Backend',
    'Java': 'Backend',
    'Spring': 'Backend',
    'Spring Boot': 'Backend',
    'Laravel': 'Backend',
    'Ruby on Rails': 'Backend',
    'C#': 'Backend',
    '.NET': 'Backend',
    'ASP.NET': 'Backend',
    'Go': 'Backend',
    'Rust': 'Backend',
    
    # Database
    'MongoDB': 'Database',
    'PostgreSQL': 'Database',
    'MySQL': 'Database',
    'Redis': 'Database',
    'Cassandra': 'Database',
    'Elasticsearch': 'Database',
    
    # Cloud
    'AWS': 'Cloud',
    'Azure': 'Cloud',
    'GCP': 'Cloud',
    'Google Cloud': 'Cloud',
    
    # DevOps
    'Docker': 'DevOps',
    'Kubernetes': 'DevOps',
    'Jenkins': 'DevOps',
    'Git': 'DevOps',
    'CI/CD': 'DevOps',
    
    # Mobile
    'Flutter': 'Mobile',
    'React Native': 'Mobile',
    'Swift': 'Mobile',
    'SwiftUI': 'Mobile',
    'Kotlin': 'Mobile',
    'Android': 'Mobile',
    'iOS': 'Mobile',
    
    # AI/ML
    'Machine Learning': 'AI/ML',
    'Deep Learning': 'AI/ML',
    'TensorFlow': 'AI/ML',
    'PyTorch': 'AI/ML',
    'ChatGPT': 'AI/ML',
    'Large Language Models': 'AI/ML',
    'Generative AI': 'AI/ML',
    'LLM': 'AI/ML',
}


def get_skill_category(skill_name):
    """
    Get category for a skill
    
    Args:
        skill_name: Name of the skill
        
    Returns:
        Category name or 'Other'
    """
    return SKILL_CATEGORIES.get(skill_name, 'Other')

# Test
if __name__ == "__main__":
    SEP = "=" * 70  # Define separator once
    
    print(SEP)
    print("SKILL NORMALIZATION - HYBRID APPROACH")
    print(SEP)
    
    # Test rule-based
    test_cases = [
        ("Git", "Git"),
        ("GIT", "Git"),
        ("HTML", "HTML"),
        ("html", "HTML"),
        ("React.js", "React"),
        ("MongoDB", "MongoDB"),
    ]
    
    print("\nRule-Based Normalization:")
    print("-" * 70)
    for input_val, expected in test_cases:
        result = normalize_skill(input_val)
        status = "✓" if result == expected else "✗"
        print(f"{status} {input_val:20} → {result}")
    
    # Test similarity detection
    print(f"\nAutomatic Similarity Detection:")
    print("-" * 70)
    
    test_skills = [
        "React", "ReactJS", "React.js",
        "Node.js", "NodeJS",
        "HTML", "Html", "html",
        "Python", "JavaScript"
    ]
    
    similar_groups = find_similar_skills(test_skills, threshold=0.8)
    
    for i, group in enumerate(similar_groups, 1):
        print(f"\nGroup {i}:")
        for skill in group:
            print(f"  • {skill}")
        print(f"  → Canonical: {group[0]}")
    
    print("\n" + SEP)