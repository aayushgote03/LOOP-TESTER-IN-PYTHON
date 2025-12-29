# SplitVault - Tech Stack Justification Script

**Project:** SplitVault - Smart Expense Splitting Application  
**Made by:** Aayush J. Gote  
**Date:** December 29, 2024  
**Purpose:** Detailed explanation of technology choices  

---

## 🎤 COMPLETE TECH STACK JUSTIFICATION SCRIPT

### **INTRODUCTION**

**"One of the most important decisions in any software project is choosing the right technology stack. For SplitVault, I carefully evaluated multiple options before settling on Next.js, Flask, and MongoDB. Let me walk you through my reasoning for each choice and the alternatives I considered."**

---

## 🎨 FRONTEND: Next.js 14 with TypeScript

### **Why I Chose Next.js**

**"For the frontend, I chose Next.js 14, and here's why:**

### **1. Server-Side Rendering (SSR) & Performance**
- **Benefit:** Next.js provides automatic SSR and static site generation, which improves initial page load times
- **For SplitVault:** The dashboard and group pages load faster because critical data can be pre-rendered
- **SEO Advantage:** Although SplitVault is a web app (not content-focused), SSR ensures search engines can properly index public pages
- **Metric:** First Contentful Paint (FCP) is typically 40-50% faster compared to pure client-side React

### **2. Built-in API Routes**
- **Benefit:** Next.js includes API routes that act as a backend proxy layer
- **For SplitVault:** I use `/app/api/*` routes to proxy requests to the Flask backend
- **Advantages:**
  - Hides the Flask backend URL from the client (security)
  - Allows me to add middleware (authentication, rate limiting) in the future
  - Provides a unified deployment (frontend + API proxy in one)
  - CORS issues are eliminated because requests appear to come from the same origin

### **3. File-Based Routing**
- **Benefit:** Automatic routing based on file structure
- **For SplitVault:** 
  - `/app/groups/page.tsx` → `/groups` route
  - `/app/group/[id]/page.tsx` → `/group/123` dynamic route
- **Developer Experience:** No need to configure React Router manually, reducing boilerplate

### **4. TypeScript Integration**
- **Benefit:** First-class TypeScript support out of the box
- **For SplitVault:** Type safety prevents bugs, especially when handling API responses
- **Example:** I defined interfaces for User, Group, Expense, Edge - the compiler catches type mismatches before runtime

### **5. Modern React Features**
- **Benefit:** Supports React Server Components, Suspense, and latest React features
- **For SplitVault:** I can use async/await directly in components for data fetching
- **Future-Proof:** Next.js stays updated with React's evolution

### **6. Developer Experience**
- **Fast Refresh:** Changes appear instantly without losing component state
- **Built-in Optimization:** Automatic code splitting, image optimization, font optimization
- **Zero Config:** Works out of the box with sensible defaults

### **Alternatives I Considered:**

**Create React App (CRA):**
- ❌ No SSR (slower initial load)
- ❌ No built-in API routes
- ❌ Requires manual routing setup
- ❌ Less optimized production builds

**Vite + React:**
- ✅ Faster development server
- ❌ No SSR without additional setup
- ❌ No API routes
- ❌ More configuration needed

**Vue.js / Nuxt.js:**
- ✅ Similar features to Next.js
- ❌ Smaller ecosystem than React
- ❌ Less industry demand (React is more marketable)

**Angular:**
- ✅ Full-featured framework
- ❌ Steeper learning curve
- ❌ Heavier bundle size
- ❌ Overkill for this project size

**Conclusion:** Next.js provided the best balance of performance, developer experience, and modern features for a full-stack application like SplitVault."

---

## 🔧 BACKEND: Flask 3.0 (Python)

### **Why I Chose Flask**

**"For the backend, I chose Flask, a Python micro-framework. Here's my reasoning:**

### **1. Simplicity and Flexibility**
- **Benefit:** Flask is minimalist - it gives you the essentials and lets you add what you need
- **For SplitVault:** I only needed REST API endpoints, not a full MVC framework
- **Control:** I could structure the code exactly how I wanted (Blueprint pattern)
- **Learning Curve:** Quick to get started, but powerful enough for production

### **2. Python's Strengths**
- **Algorithm Implementation:** The debt simplification algorithm was easier to implement in Python
- **Readability:** Python's syntax is clean and self-documenting
- **Libraries:** Rich ecosystem for data manipulation (though I kept dependencies minimal)
- **Rapid Development:** Python allows fast iteration during development

### **3. Blueprint Pattern for Modularity**
- **Benefit:** Flask Blueprints allow organizing routes into logical modules
- **For SplitVault:**
  ```
  auth_bp      → /register, /login
  groups_bp    → /groups/create, /add_expense, /groups/balances
  simplify_bp  → /groups/simplify_debts
  ```
- **Maintainability:** Each blueprint is self-contained and testable
- **Scalability:** Easy to add new blueprints as features grow

### **4. PyMongo Integration**
- **Benefit:** PyMongo is the official MongoDB driver for Python
- **For SplitVault:** Seamless integration with MongoDB
- **Pythonic API:** Queries feel natural in Python
- **Example:**
  ```python
  db.edges.find({"group_id": group_id, "status": "PENDING"})
  ```

### **5. Werkzeug Security**
- **Benefit:** Built-in security utilities
- **For SplitVault:** Used `generate_password_hash()` and `check_password_hash()` for bcrypt
- **Trusted:** Werkzeug is battle-tested and secure

### **6. Lightweight and Fast**
- **Benefit:** Flask has minimal overhead
- **For SplitVault:** API responses are fast (typically < 100ms)
- **Resource Efficient:** Low memory footprint, suitable for serverless deployment

### **7. Deployment Flexibility**
- **Benefit:** Flask can deploy anywhere
- **For SplitVault:** 
  - Vercel Serverless Functions (current setup)
  - Railway, Render, Heroku
  - Docker containers
  - Traditional servers (Gunicorn + Nginx)

### **Alternatives I Considered:**

**Django:**
- ✅ Full-featured (ORM, admin panel, auth)
- ❌ Too heavy for a REST API-only backend
- ❌ Opinionated structure (less flexibility)
- ❌ Slower development for simple APIs
- **Verdict:** Overkill for SplitVault's needs

**FastAPI:**
- ✅ Modern, async support
- ✅ Automatic API documentation (Swagger)
- ✅ Type hints and validation (Pydantic)
- ❌ I wanted to focus on core functionality, not async complexity
- ❌ Slightly newer (less mature than Flask)
- **Verdict:** Great choice, but Flask was sufficient

**Express.js (Node.js):**
- ✅ JavaScript everywhere (same language as frontend)
- ✅ Large ecosystem (npm)
- ❌ Callback hell / async complexity
- ❌ Python is better for algorithms
- ❌ I wanted to demonstrate polyglot skills
- **Verdict:** Valid choice, but I preferred Python

**Spring Boot (Java):**
- ✅ Enterprise-grade, robust
- ❌ Verbose code
- ❌ Slower development
- ❌ Heavier resource usage
- **Verdict:** Too heavyweight for this project

**Conclusion:** Flask offered the perfect balance of simplicity, flexibility, and Python's strengths for implementing business logic and algorithms."

---

## 🗄️ DATABASE: MongoDB Atlas

### **Why I Chose MongoDB**

**"For the database, I chose MongoDB Atlas, a cloud-hosted NoSQL database. Here's why:**

### **1. Document Model Fits the Domain**
- **Benefit:** MongoDB stores data as JSON-like documents
- **For SplitVault:**
  - **Groups** naturally contain arrays of members and expenses
  - **Expenses** have variable participant structures (equal, exact, percent splits)
  - **Users** have arrays of group IDs
- **Schema Flexibility:** Different split types require different participant structures:
  ```javascript
  // Equal split
  participants: [{email: "alice@example.com"}]
  
  // Exact split
  participants: [{email: "alice@example.com", amount: 50.00}]
  
  // Percent split
  participants: [{email: "alice@example.com", percentage: 40}]
  ```
- **In SQL:** This would require complex joins or JSON columns

### **2. Embedded Documents**
- **Benefit:** Related data can be stored together
- **For SplitVault:**
  - Group document contains arrays of expense IDs and edge IDs
  - Reduces need for joins
  - Faster reads (single query instead of multiple joins)
- **Example:**
  ```javascript
  {
    "_id": "group123",
    "name": "Weekend Trip",
    "members": ["alice@example.com", "bob@example.com"],
    "expenses": ["exp1", "exp2", "exp3"],
    "edges": ["edge1", "edge2"]
  }
  ```

### **3. Scalability**
- **Benefit:** MongoDB scales horizontally (sharding)
- **For SplitVault:** As users grow, I can shard by group_id or user_id
- **Atlas Features:** Automatic scaling, backups, monitoring
- **Future-Proof:** Can handle millions of users without major refactoring

### **4. Cloud-Native (Atlas)**
- **Benefit:** Fully managed, no server maintenance
- **For SplitVault:**
  - Automatic backups
  - Built-in monitoring and alerts
  - Global distribution (low latency worldwide)
  - Free tier for development
- **DevOps Savings:** No need to manage database servers

### **5. Flexible Schema Evolution**
- **Benefit:** Can add fields without migrations
- **For SplitVault:** When I added the `is_simplified` field to edges, no migration was needed
- **Agile Development:** Faster iteration during development
- **Backward Compatibility:** Old documents still work

### **6. Powerful Query Language**
- **Benefit:** Rich query operators
- **For SplitVault:**
  ```javascript
  // Find all pending debts where user owes money
  db.edges.find({
    "sender_email": user_email,
    "status": "PENDING",
    "group_id": group_id
  })
  
  // Aggregation for complex queries
  db.expenses.aggregate([
    {$match: {group_id: "group123"}},
    {$group: {_id: "$payer_email", total: {$sum: "$amount"}}}
  ])
  ```

### **7. Indexing for Performance**
- **Benefit:** Supports various index types
- **For SplitVault:** I created indexes on:
  - `users.email` (unique)
  - `edges.group_id` + `edges.status` (compound)
  - `expenses.payer_email`
  - `activity_logs.created_at` (descending)
- **Result:** Queries are fast even with thousands of records

### **8. Atomic Operations**
- **Benefit:** Operations like `$push`, `$pull`, `$inc` are atomic
- **For SplitVault:**
  ```javascript
  // Atomically add expense to group
  db.groups.update_one(
    {"_id": group_id},
    {"$push": {"expenses": expense_id}}
  )
  ```
- **Concurrency:** Safe for multiple users updating the same group

### **Alternatives I Considered:**

**PostgreSQL:**
- ✅ ACID transactions (stronger consistency)
- ✅ Mature, battle-tested
- ✅ Better for complex joins
- ❌ Rigid schema (requires migrations)
- ❌ JSON columns are less elegant than MongoDB documents
- ❌ Harder to scale horizontally
- **Verdict:** Great for financial apps, but MongoDB's flexibility was more valuable here

**MySQL:**
- ✅ Widely used, well-documented
- ❌ Similar drawbacks to PostgreSQL
- ❌ Less modern than PostgreSQL
- **Verdict:** PostgreSQL would be better if I chose SQL

**Firebase Firestore:**
- ✅ Real-time updates out of the box
- ✅ Easy authentication integration
- ❌ Vendor lock-in (Google)
- ❌ Limited query capabilities
- ❌ Expensive at scale
- **Verdict:** Good for rapid prototyping, but less control

**DynamoDB:**
- ✅ Serverless, auto-scaling
- ❌ Complex pricing model
- ❌ Limited query flexibility
- ❌ AWS lock-in
- **Verdict:** Great for AWS-native apps, but MongoDB is more flexible

**Redis:**
- ✅ Extremely fast (in-memory)
- ❌ Not suitable as primary database
- ❌ Data persistence is secondary
- **Verdict:** Good for caching, not primary storage

**Conclusion:** MongoDB Atlas provided the best combination of flexibility, scalability, and developer experience for SplitVault's data model."

---

## 🎨 STYLING: Tailwind CSS

### **Why I Chose Tailwind CSS**

**"For styling, I chose Tailwind CSS, a utility-first CSS framework:**

### **1. Utility-First Approach**
- **Benefit:** Style components directly in JSX with utility classes
- **For SplitVault:**
  ```jsx
  <button className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg">
    Add Expense
  </button>
  ```
- **Speed:** No need to switch between files or think of class names
- **Consistency:** Predefined spacing, colors, and sizes

### **2. Responsive Design**
- **Benefit:** Built-in responsive modifiers
- **For SplitVault:**
  ```jsx
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  ```
- **Mobile-First:** Works perfectly on all screen sizes

### **3. Dark Mode Support**
- **Benefit:** Easy dark mode implementation
- **For SplitVault:** Dark theme with `dark:` prefix
- **Modern:** Matches user expectations for modern apps

### **4. Small Bundle Size**
- **Benefit:** PurgeCSS removes unused styles in production
- **For SplitVault:** Final CSS is ~10KB (vs 100KB+ for Bootstrap)
- **Performance:** Faster page loads

### **5. Customization**
- **Benefit:** Easy to customize in `tailwind.config.js`
- **For SplitVault:** Custom emerald green color scheme
- **Brand Consistency:** Maintains design system

### **Alternatives:**
- **Bootstrap:** Too opinionated, harder to customize
- **Material-UI:** Heavy, React-specific
- **Vanilla CSS:** Too much boilerplate
- **CSS Modules:** Good, but less efficient than Tailwind

**Conclusion:** Tailwind provided rapid development with a modern, consistent design."

---

## 🔗 INTEGRATION: How It All Works Together

### **The Full Stack Flow**

**"Here's how all these technologies work together in SplitVault:**

```
User Action (Browser)
    ↓
Next.js Frontend (TypeScript + Tailwind)
    ↓
Next.js API Route (Proxy Layer)
    ↓
Flask Backend (Python + Blueprints)
    ↓
PyMongo Driver
    ↓
MongoDB Atlas (Cloud Database)
    ↓
Response flows back up the chain
```

### **Example: Adding an Expense**

1. **User fills form** → React component with Tailwind styling
2. **Form submission** → TypeScript validates data
3. **API call** → `fetch('/api/add_expense', {...})`
4. **Next.js proxy** → Forwards to Flask at `http://localhost:5000/add_expense`
5. **Flask endpoint** → Validates, calculates splits
6. **PyMongo** → Inserts expense, creates edges, updates group
7. **MongoDB** → Stores data with indexes for fast retrieval
8. **Response** → JSON flows back through the chain
9. **UI update** → React re-renders with new data

### **Why This Stack is Cohesive:**

1. **TypeScript + Python:** Both are strongly-typed, reducing bugs
2. **Next.js + Flask:** Clear separation of concerns (presentation vs. logic)
3. **MongoDB + Python:** PyMongo's API is Pythonic and intuitive
4. **Tailwind + Next.js:** Perfect integration, no configuration needed
5. **All Modern:** Each technology is actively maintained and industry-standard

---

## 🎯 ALTERNATIVE STACKS I CONSIDERED

### **Option 1: MERN Stack (Mongo, Express, React, Node)**
```
React + Express.js + MongoDB + Node.js
```
**Pros:**
- ✅ JavaScript everywhere
- ✅ Large ecosystem

**Cons:**
- ❌ Callback complexity
- ❌ Less suitable for algorithms
- ❌ Wanted to show polyglot skills

**Verdict:** Valid, but I preferred Python for backend logic

---

### **Option 2: Django Full Stack**
```
Django + Django Templates + PostgreSQL
```
**Pros:**
- ✅ All-in-one framework
- ✅ Built-in admin panel

**Cons:**
- ❌ Monolithic (harder to separate frontend/backend)
- ❌ Less modern frontend experience
- ❌ Overkill for API-only backend

**Verdict:** Too heavy and opinionated

---

### **Option 3: JAMstack (Next.js + Serverless + Firestore)**
```
Next.js + Vercel Functions + Firebase
```
**Pros:**
- ✅ Fully serverless
- ✅ Real-time updates

**Cons:**
- ❌ Vendor lock-in
- ❌ Less control over backend logic
- ❌ Complex pricing

**Verdict:** Good for rapid prototyping, but less educational

---

### **Option 4: Modern Python Stack (FastAPI + React + PostgreSQL)**
```
React + FastAPI + PostgreSQL
```
**Pros:**
- ✅ Modern async Python
- ✅ Auto-generated API docs
- ✅ Strong typing (Pydantic)

**Cons:**
- ❌ More complex than Flask
- ❌ Async might be overkill
- ❌ PostgreSQL requires migrations

**Verdict:** Great choice, but Flask was simpler for this scope

---

## 📊 TECH STACK COMPARISON TABLE

| Criteria | My Choice | Why | Alternative |
|----------|-----------|-----|-------------|
| **Frontend Framework** | Next.js | SSR, API routes, file routing | Vite + React |
| **Language (FE)** | TypeScript | Type safety, better DX | JavaScript |
| **Styling** | Tailwind CSS | Utility-first, fast development | CSS Modules |
| **Backend Framework** | Flask | Lightweight, flexible | FastAPI, Express |
| **Language (BE)** | Python | Algorithm-friendly, readable | Node.js, Java |
| **Database** | MongoDB | Document model, flexible schema | PostgreSQL |
| **Cloud DB** | MongoDB Atlas | Managed, scalable | Self-hosted |
| **Auth** | Werkzeug (bcrypt) | Built-in, secure | JWT, OAuth |
| **Deployment** | Vercel + Atlas | Serverless, easy | Docker + AWS |

---

## 🎓 WHAT I LEARNED FROM THESE CHOICES

### **1. Right Tool for the Job**
- Not every project needs the heaviest framework
- Flask was perfect for a REST API
- Next.js provided modern features without complexity

### **2. Developer Experience Matters**
- Fast refresh, TypeScript errors, Tailwind autocomplete
- These tools made development enjoyable and productive

### **3. Scalability Considerations**
- MongoDB Atlas can scale horizontally
- Next.js and Flask both support serverless deployment
- The architecture can grow with the user base

### **4. Learning Opportunity**
- This stack let me demonstrate full-stack skills
- Python + TypeScript shows language versatility
- NoSQL + REST API are industry-relevant

### **5. Production-Ready**
- Every technology chosen is battle-tested
- All have strong communities and documentation
- The stack is used by real companies in production

---

## 🚀 FUTURE TECH ADDITIONS

**As SplitVault grows, I would add:**

1. **Redis** - For caching frequently accessed data
2. **WebSockets** - For real-time updates (Socket.io or Pusher)
3. **Stripe API** - For actual payment processing
4. **SendGrid** - For email notifications
5. **Sentry** - For error tracking and monitoring
6. **Jest + Pytest** - For comprehensive testing
7. **Docker** - For consistent deployment environments
8. **GitHub Actions** - For CI/CD pipeline

---

## 💡 KEY TAKEAWAY

**"The tech stack I chose for SplitVault represents a modern, scalable, and maintainable architecture:**

- ✅ **Next.js** for a performant, SEO-friendly frontend
- ✅ **Flask** for a lightweight, flexible backend
- ✅ **MongoDB** for a schema-flexible, scalable database
- ✅ **TypeScript** for type safety and better developer experience
- ✅ **Tailwind** for rapid, consistent UI development

**Each choice was deliberate, considering:**
- Project requirements
- Development speed
- Scalability
- Learning value
- Industry relevance

**This stack allowed me to build a production-ready application efficiently while demonstrating full-stack proficiency."**

---

## 🎤 CLOSING STATEMENT

**"In summary, I didn't just pick popular technologies randomly. Each choice was made after considering:**

1. **Project Needs:** What does SplitVault require?
2. **Performance:** Will it be fast and scalable?
3. **Developer Experience:** Can I build efficiently?
4. **Maintainability:** Can I easily add features?
5. **Industry Relevance:** Are these skills valuable?

**The result is a cohesive, modern tech stack that powers a fully functional expense splitting application. I'm confident this architecture can scale from a demo project to a production application serving thousands of users.**

**I'm happy to discuss any specific technology choice in more detail or explain trade-offs I considered."**

---

## 📚 REFERENCES & RESOURCES

**Technologies Used:**
- [Next.js Documentation](https://nextjs.org/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [MongoDB Atlas](https://www.mongodb.com/atlas)
- [Tailwind CSS](https://tailwindcss.com/)
- [TypeScript](https://www.typescriptlang.org/)
- [PyMongo](https://pymongo.readthedocs.io/)

**Learning Resources:**
- Next.js tutorials and examples
- Flask Mega-Tutorial by Miguel Grinberg
- MongoDB University courses
- Real Python tutorials

---

**Made by:** Aayush J. Gote  
**Date:** December 29, 2024  
**Project:** SplitVault Tech Stack Justification  
**Purpose:** Interview preparation - explaining technology choices
