import React, { useState } from 'react';
import {
    signInWithEmailAndPassword,
    createUserWithEmailAndPassword,
    sendPasswordResetEmail
} from 'firebase/auth';
import { auth } from '../firebase';

export default function Login() {
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [resetSent, setResetSent] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setLoading(true);
        try {
            if (isLogin) {
                await signInWithEmailAndPassword(auth, email, password);
            } else {
                await createUserWithEmailAndPassword(auth, email, password);
            }
        } catch (err) {
            setError(err.message.replace('Firebase: ', ''));
        }
        setLoading(false);
    };


    const handleForgotPassword = async () => {
        if (!email) {
            setError('Please enter your email address first.');
            return;
        }
        setError(null);
        setLoading(true);
        try {
            await sendPasswordResetEmail(auth, email);
            setResetSent(true);
            setTimeout(() => setResetSent(false), 5000);
        } catch (err) {
            setError(err.message.replace('Firebase: ', ''));
        }
        setLoading(false);
    };

    return (
        <div className="login-container">
            <div className="login-card">
                <div className="login-header">
                    <div className="login-logo">🚀</div>
                    <h1>{isLogin ? 'Welcome Back' : 'Create Account'}</h1>
                    <p>{isLogin ? 'Sign in to access AI DAAAS' : 'Join the AI-powered analytics hub'}</p>
                </div>

                <form className="login-form" onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Email Address</label>
                        <input
                            type="email"
                            placeholder="name@company.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>
                    <div className="form-group">
                        <div className="flex-between">
                            <label>Password</label>
                            {isLogin && (
                                <button type="button" className="link-btn small-text" onClick={handleForgotPassword}>
                                    Forgot Password?
                                </button>
                            )}
                        </div>
                        <input
                            type="password"
                            placeholder="••••••••"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>

                    {error && <div className="auth-error">❌ {error}</div>}
                    {resetSent && <div className="auth-success">✅ Password reset email sent! Check your inbox.</div>}

                    <button className="btn btn-primary btn-full" type="submit" disabled={loading}>
                        {loading ? 'Processing...' : (isLogin ? 'Sign In' : 'Create Account')}
                    </button>
                </form>


                <div className="login-footer">
                    {isLogin ? "Don't have an account?" : "Already have an account?"}{' '}
                    <button className="link-btn" onClick={() => setIsLogin(!isLogin)}>
                        {isLogin ? 'Sign Up' : 'Log In'}
                    </button>
                </div>
            </div>

            <style jsx>{`
                .login-container {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                    background: var(--bg);
                    padding: 1rem;
                }
                .login-card {
                    width: 100%;
                    max-width: 400px;
                    background: var(--surface);
                    border: 1px solid var(--border);
                    border-radius: 20px;
                    padding: 2.5rem;
                    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
                }
                .login-header {
                    text-align: center;
                    margin-bottom: 2rem;
                }
                .login-logo {
                    font-size: 3rem;
                    margin-bottom: 1rem;
                }
                .login-header h1 {
                    font-size: 1.5rem;
                    margin-bottom: 0.5rem;
                    color: var(--text);
                }
                .login-header p {
                    color: var(--text-muted);
                    font-size: 0.9rem;
                }
                .login-form {
                    display: flex;
                    flex-direction: column;
                    gap: 1.25rem;
                }
                .form-group {
                    display: flex;
                    flex-direction: column;
                    gap: 0.5rem;
                }
                .form-group label {
                    font-size: 0.8rem;
                    font-weight: 600;
                    color: var(--text-muted);
                }
                .form-group input {
                    background: var(--surface2);
                    border: 1px solid var(--border);
                    border-radius: 8px;
                    padding: 0.75rem 1rem;
                    color: var(--text);
                    font-size: 0.9rem;
                }
                .form-group input:focus {
                    outline: none;
                    border-color: var(--accent);
                }
                .auth-error {
                    color: var(--danger);
                    font-size: 0.8rem;
                    background: rgba(239, 68, 68, 0.1);
                    padding: 0.75rem;
                    border-radius: 8px;
                    border: 1px solid rgba(239, 68, 68, 0.2);
                }
                .auth-success {
                    color: #10b981;
                    font-size: 0.8rem;
                    background: rgba(16, 185, 129, 0.1);
                    padding: 0.75rem;
                    border-radius: 8px;
                    border: 1px solid rgba(16, 185, 129, 0.2);
                }
                .flex-between {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .small-text {
                    font-size: 0.75rem;
                }
                .login-footer {
                    margin-top: 2rem;
                    text-align: center;
                    font-size: 0.9rem;
                    color: var(--text-muted);
                }
                .link-btn {
                    background: none;
                    border: none;
                    color: var(--accent);
                    font-weight: 600;
                    cursor: pointer;
                    padding: 0;
                }
                .link-btn:hover {
                    text-decoration: underline;
                }
            `}</style>
        </div>
    );
}
