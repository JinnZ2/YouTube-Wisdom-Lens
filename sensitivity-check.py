def cultural_sensitivity_check(text):
    protected_terms = {
        'indigenous': ['sacred', 'ceremony', 'elder wisdom'],
        'spiritual': ['ritual', 'initiation', 'mystery']
    }
    
    warnings = []
    for category, terms in protected_terms.items():
        found = [t for t in terms if t in text.lower()]
        if found:
            warnings.append(f"Contains protected {category} terms: {', '.join(found)}")
    
    return warnings if warnings else "No sensitive terms detected"
