/*
 * NOTE: This code was generated with AI assistance for training purposes.
 * 
 * This file is part of Atmosera's AI Adoption Training.
 * It contains intentional patterns (code smells, technical debt, security issues, etc.)\n * designed to help learners practice using AI tools like GitHub Copilot and Amazon Q
 * for code analysis, refactoring, testing, and documentation.
 * 
 * Activity: Documentation Workflows - From Code Comments to Architecture
 * Purpose: TypeScript AuthService parity with documentation practice
 * Focus Area: Security strengthening (bcrypt/JWT), tests, input validation
 * Instructions: Strengthen security, add tests, and validate inputs before production.
 *
 * AuthService (TypeScript) parity of Python version.
 *
 * Responsibilities:
 * - Register users (salted HMAC-SHA256 password hashes; demo only).
 * - Authenticate and issue opaque time-bound tokens.
 * - Refresh and revoke tokens.
 *
 * Environment Variables (conceptual): AUTH_TOKEN_TTL, AUTH_JWT_SECRET.
 * Security: Replace hashing with bcrypt/argon2; add rate limiting & lockout.
 */
import crypto from 'crypto';

export interface AuthToken { token: string; subject: string; expiresAt: number; }

export class AuthService {
  private users: Record<string, string> = {}; // username -> salt$hash
  private tokens: Record<string, AuthToken> = {}; // token -> AuthToken
  private secret: string;
  private ttl: number;

  constructor() {
    this.secret = process.env.AUTH_JWT_SECRET || 'demo-secret';
    this.ttl = parseInt(process.env.AUTH_TOKEN_TTL || '3600', 10);
  }

  register(username: string, password: string): void {
    if (this.users[username]) throw new Error('user already exists');
    const salt = crypto.randomBytes(8).toString('hex');
    const hash = this.hash(password, salt);
    this.users[username] = `${salt}$${hash}`;
  }

  authenticate(username: string, password: string): AuthToken {
    const stored = this.users[username];
    if (!stored) throw new Error('invalid credentials');
    const [salt, hashed] = stored.split('$');
    if (this.hash(password, salt) !== hashed) throw new Error('invalid credentials');
    const token = crypto.randomBytes(24).toString('base64url');
    const expiresAt = Math.floor(Date.now() / 1000) + this.ttl;
    const authToken: AuthToken = { token, subject: username, expiresAt };
    this.tokens[token] = authToken;
    return authToken;
  }

  refresh(token: string): AuthToken {
    const existing = this.tokens[token];
    if (!existing) throw new Error('invalid token');
    const now = Math.floor(Date.now() / 1000);
    if (existing.expiresAt < now) throw new Error('token expired');
    existing.expiresAt = now + this.ttl;
    return existing;
  }

  revoke(token: string): void {
    delete this.tokens[token];
  }

  private hash(password: string, salt: string): string {
    const h = crypto.createHmac('sha256', this.secret);
    h.update(`${salt}:${password}`);
    return h.digest('hex');
  }
}

// Demo
if (require.main === module) {
  const svc = new AuthService();
  svc.register('alice', 'wonderland');
  const token = svc.authenticate('alice', 'wonderland');
  console.log('Issued token:', token);
  const refreshed = svc.refresh(token.token);
  console.log('Refreshed expiresAt:', refreshed.expiresAt);
  svc.revoke(token.token);
  console.log('Revoked token; valid?', !!svc['tokens'][token.token]);
}
