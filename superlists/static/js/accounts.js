// Supabase authentication JavaScript with Email Magic Link
var Superlists = (function() {
    'use strict';

    var supabaseClient = null;
    var currentUser = null;
    var config = {
        authEndpoint: '/accounts/auth/',
        logoutEndpoint: '/accounts/logout/'
    };

    function initialize(supabaseUrl, apiKey, configOverride) {
        // Initialize Supabase client
        if (window.supabase) {
            supabaseClient = window.supabase.createClient(supabaseUrl, apiKey);
        }

        // Override config if provided
        if (configOverride) {
            Object.assign(config, configOverride);
        }

        // Initialize auth state tracking
        if (supabaseClient) {
            setupAuthListeners();
        }

        // Set up login link
        setupLoginLink();
    }

    function setupAuthListeners() {
        // Check current session
        supabaseClient.auth.getSession().then(({ data: { session } }) => {
            if (session) {
                currentUser = session.user.email;
                updateLoginLink();
            }
        });

        // Listen for auth changes
        supabaseClient.auth.onAuthStateChange((event, session) => {
            if (event === 'SIGNED_IN') {
                currentUser = session.user.email;
                sendEmailToBackend(session.user.email);
                updateLoginLink();
                hideLoginModal();
            } else if (event === 'SIGNED_OUT') {
                currentUser = null;
                updateLoginLink();
            }
        });
    }

    function setupLoginLink() {
        var loginLink = document.getElementById('login');
        if (loginLink) {
            loginLink.addEventListener('click', function(e) {
                e.preventDefault();

                if (currentUser) {
                    // User is logged in, logout
                    logout();
                } else {
                    // User is not logged in, show login modal
                    showLoginModal();
                }
            });
        }

        // Setup login form
        var loginForm = document.getElementById('login-form');
        if (loginForm) {
            loginForm.addEventListener('submit', function(e) {
                e.preventDefault();
                var email = document.getElementById('email').value;
                if (email) {
                    signInWithEmail(email);
                }
            });
        }
    }

    function showLoginModal() {
        var modal = document.getElementById('login-modal');
        if (modal) {
            modal.style.display = 'block';
            document.getElementById('email').focus();
        }
    }

    function hideLoginModal() {
        var modal = document.getElementById('login-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    function signInWithEmail(email) {
        var messageDiv = document.getElementById('login-message');
        messageDiv.style.display = 'block';
        messageDiv.innerHTML = '<div class="alert alert-info">正在发送登录链接...</div>';

        // Use Supabase's OTP (One-Time Password) magic link
        supabaseClient.auth.signInWithOtp({
            email: email,
            options: {
                emailRedirectTo: window.location.origin
            }
        }).then(({ data, error }) => {
            if (error) {
                messageDiv.innerHTML = '<div class="alert alert-danger">登录失败: ' + error.message + '</div>';
                console.error('Login error:', error);
            } else {
                messageDiv.innerHTML = '<div class="alert alert-success">✅ 登录链接已发送到 ' + email + '<br/>请检查您的邮箱并点击链接登录</div>';
                // Clear the form
                document.getElementById('email').value = '';
            }
        });
    }

    function logout() {
        supabaseClient.auth.signOut().then(({ error }) => {
            if (error) {
                console.error('Logout error:', error);
            } else {
                // Send logout to backend
                fetch(config.logoutEndpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'same-origin'
                }).then(() => {
                    window.location.reload();
                });
            }
        });
    }

    function sendEmailToBackend(email) {
        fetch(config.authEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: email }),
            credentials: 'same-origin'
        }).catch(error => {
            console.error('Error sending email to backend:', error);
        });
    }

    function updateLoginLink() {
        var authSection = document.getElementById('auth-section');
        if (!authSection) return;

        if (currentUser) {
            authSection.innerHTML = '<a id="login" class="navbar-link" href="#">Sign out (' + currentUser + ')</a>';
            // Re-attach event listener
            setupLoginLink();
        } else {
            authSection.innerHTML = '<a id="login" class="navbar-link" href="#">Sign in</a>';
            // Re-attach event listener
            setupLoginLink();
        }
    }

    return {
        initialize: initialize
    };
})();
