def custom_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    try:
        branding = SchoolBranding.get_config()
    except Exception:
        branding = None
    
    if request.method == 'POST':
        # Clean username input manually to enforce lowercase and strip spaces
        post_data = request.POST.copy()
        if 'username' in post_data:
            post_data['username'] = post_data['username'].strip().lower()

        form = AuthenticationForm(request, data=post_data)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password. Note: Usernames are case-insensitive and lowercased.")
    else:
        form = AuthenticationForm()

    return render(request, 'portal/login.html', {'form': form, 'branding': branding})