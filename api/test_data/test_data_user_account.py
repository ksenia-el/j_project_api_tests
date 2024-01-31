class TestData:

    invalid_emails = [
        "plainaddress",  # Missing '@' symbol and domain
        "username@",  # Missing domain part
        "username@.com",  # Leading dot in domain
        "user..name@domain.com",  # Consecutive dots in local part
        "username@domain..com",  # Consecutive dots in domain part
        "username@domain_com",  # Underscore in domain part
        ".username@domain.com",  # Leading dot in local part
        "username@-domain.com",  # Leading dash in domain part
        "username@domain-.com",  # Trailing dash in domain part
        "username@domain com",  # Space in domain part
        "username@do!main.com",  # Special character in domain part
        "username@",  # Missing domain part entirely
        "username@domain@domain.com",  # Multiple '@' symbols
        "username@domain",  # Missing top-level domain
        "username@-domain.com",  # Domain starts with a hyphen
        "username@domain-.com",  # Domain ends with a hyphen
        "username@domain.com.",  # Trailing dot in domain
        "username@domain..com",  # Consecutive dots in the domain
        "username@domain.com/a",  # Path after domain
        "username@domain..com",  # Consecutive dots in the domain
        "username@domain_.com",  # Underscore in domain
        "username@domain!com",  # Exclamation mark in domain
        "username@domain#com",  # Hash in domain
        "username@domain$com",  # Dollar sign in domain
        "username@domain%com",  # Percent sign in domain
        "username@domain^com",  # Caret in domain
        "username@domain&com",  # Ampersand in domain
        "username@domain*com",  # Asterisk in domain
        "username@domain(com",  # Open parenthesis in domain
        "username@domain)com",  # Close parenthesis in domain
        "username@domain+com",  # Plus sign in domain
        "username@domain=com",  # Equals sign in domain
        "username@domain[com",  # Open bracket in domain
        "username@domain]com",  # Close bracket in domain
        "username@domain{com",  # Open brace in domain
        "username@domain}com",  # Close brace in domain
        "username@domain|com",  # Vertical bar in domain
        "username@domain\\com",  # Backslash in domain
        "username@domain:com",  # Colon in domain
        "username@domain;com",  # Semicolon in domain
        "username@domain'com",  # Apostrophe in domain
        "username@domain\"com",  # Quotation mark in domain
        "username@domain<com",  # Less than sign in domain
        "username@domain>com",  # Greater than sign in domain
        "username@domain,com",  # Comma in domain
    ]