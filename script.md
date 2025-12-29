# SplitVault - 10-Minute Interview Script

**Project:** SplitVault - Smart Expense Splitting Application  
**Made by:** Aayush J. Gote  
**Date:** December 29, 2024  
**Duration:** ~10 minutes  

---

## 📋 Script Structure

1. **Introduction** (1 minute)
2. **Project Overview** (1.5 minutes)
3. **Technical Architecture** (2 minutes)
4. **Backend Deep Dive** (2 minutes)
5. **Frontend Implementation** (1.5 minutes)
6. **Key Algorithm - Debt Simplification** (1.5 minutes)
7. **Challenges Faced** (1 minute)
8. **Closing & Future Scope** (30 seconds)

---

## 🎤 COMPLETE INTERVIEW SCRIPT

### **[1] INTRODUCTION (1 minute)**

**"Good morning/afternoon! Thank you for this opportunity. Today, I'm excited to present SplitVault, a full-stack expense splitting application that I developed from scratch. This project showcases my skills in modern web development, database design, algorithm implementation, and solving real-world problems.**

**SplitVault is inspired by applications like Splitwise, but I've added my own unique features, particularly a graph-based debt simplification algorithm that minimizes the number of transactions needed to settle group expenses. The application is built using Next.js for the frontend, Flask for the backend, and MongoDB Atlas as the database.**

**Let me walk you through the project in detail."**

---

### **[2] PROJECT OVERVIEW (1.5 minutes)**

**"So, what exactly is SplitVault? It's a web application designed to solve a common problem: managing shared expenses among friends, roommates, or travel groups. When multiple people share costs, tracking who owes whom can become complicated very quickly.**

**SplitVault provides the following core features:**

1. **User Authentication** - Secure registration and login with bcrypt password hashing
2. **Group Management** - Users can create expense groups and add members by email
3. **Flexible Expense Splitting** - Three split types:
   - **Equal Split** - Divide the amount equally among all participants
   - **Exact Split** - Specify custom amounts for each person
   - **Percentage Split** - Allocate costs by percentage
4. **Real-time Balance Tracking** - The system automatically calculates who owes whom after every expense
5. **Debt Settlement** - Users can make full or partial payments to settle their debts
6. **Smart Debt Simplification** - This is the star feature. Using a graph algorithm, the system can reduce the number of transactions needed to settle all debts while preserving everyone's net balance
7. **Activity Logging** - Complete audit trail of all actions for transparency

**The application is fully functional, deployed-ready, and handles complex edge cases like circular debts, partial settlements, and multi-user scenarios."**

---

### **[3] TECHNICAL ARCHITECTURE (2 minutes)**

**"Let me explain the technical architecture. SplitVault follows a modern three-tier architecture:**

**Frontend Layer:**
- Built with **Next.js 14** using TypeScript
- **Tailwind CSS** for responsive, modern UI design
- **Lucide Icons** for consistent iconography
- The frontend communicates with the backend through Next.js API routes, which act as a proxy layer

**Backend Layer:**
- Developed using **Flask 3.0**, a lightweight Python web framework
- Organized using the **Blueprint pattern** for modular code organization
- Four main blueprints:
  - `auth.py` - Handles registration and login (3 endpoints)
  - `groups.py` - Manages groups and expenses (8 endpoints)
  - `simplify.py` - Implements the debt simplification algorithm (1 endpoint)
  - `routes.py` - General routes (1 endpoint)
- **Flask-CORS** enabled for cross-origin requests during development
- **Werkzeug** for secure password hashing using bcrypt

**Database Layer:**
- **MongoDB Atlas** - Cloud-hosted NoSQL database
- Seven collections:
  1. `users` - User accounts with hashed passwords
  2. `groups` - Expense groups with members
  3. `expenses` - Individual expense records
  4. `edges` - Debt relationships (graph edges)
  5. `settlements` - Payment history
  6. `activity_logs` - Audit trail
  7. `sessions` - User session management
- **Indexes** created on frequently queried fields for performance optimization

**The data flow is:**
```
User → Next.js Frontend → Next.js API Proxy → Flask Backend → MongoDB Atlas
```

**This architecture provides clear separation of concerns, making the codebase maintainable and scalable."**

---

### **[4] BACKEND DEEP DIVE (2 minutes)**

**"Let me dive deeper into the backend implementation, which is where most of the business logic resides.**

**Database Design:**
- I used a **Singleton pattern** for the database connection to ensure a single, reusable connection instance across the application
- The `edges` collection is particularly important - it represents debts as directed graph edges where:
  - `sender_email` is the person who owes money
  - `receiver_email` is the person who is owed
  - `amount` is how much is owed
  - `status` can be PENDING, SETTLED, or SIMPLIFIED

**Data Models:**
- I implemented a **Factory pattern** for data models using static methods
- For example, the `Expense.format()` method ensures consistent data structure:
  - Validates split type (EQUAL, EXACT, or PERCENT)
  - Rounds amounts to 2 decimal places
  - Adds timestamps automatically
  - Structures participants correctly based on split type

**Key API Endpoints:**

1. **POST /add_expense** - This is the most complex endpoint:
   - Validates the expense data
   - Creates an expense document
   - Calculates individual shares based on split type
   - Creates edge documents for each debt relationship
   - Updates the group's expenses array
   - Returns updated balances
   - All operations are atomic to prevent data inconsistency

2. **POST /groups/balances** - Balance calculation:
   - Queries all PENDING edges where user is the sender (debts they owe)
   - Queries all PENDING edges where user is the receiver (debts owed to them)
   - Returns individual breakdown, not aggregated, so users can see exactly which expense created which debt
   - Calculates net balance (what they're owed minus what they owe)

3. **POST /settle_debt** - Settlement handling:
   - Supports both full and partial payments
   - For partial payments, it updates the edge amount
   - For full payments, it deletes the edge
   - Creates a settlement record for audit purposes
   - Logs the activity

**Security Implementation:**
- Passwords are hashed using **bcrypt** before storage
- Email uniqueness is enforced at the database level with unique indexes
- Authorization checks ensure only group creators can simplify debts
- Input validation on both frontend and backend prevents injection attacks"**

---

### **[5] FRONTEND IMPLEMENTATION (1.5 minutes)**

**"On the frontend side, I built a modern, responsive interface using Next.js and TypeScript.**

**Key Components:**

1. **AddExpenseModal.tsx** - A reusable modal component for adding expenses:
   - Dynamic form that changes based on selected split type
   - Real-time validation (e.g., percentages must sum to 100%)
   - Participant selection with checkboxes
   - Amount calculation preview before submission

2. **SettlementModal.tsx** - Handles debt settlements:
   - Shows all debts to a specific person
   - Allows selecting individual debts when multiple exist
   - Toggle between full and partial payment
   - Input validation for partial amounts
   - Confirmation before settlement

3. **LogoutButton.tsx** - Simple logout functionality with session cleanup

**Page Structure:**
- `/auth/signup` and `/auth/login` - Authentication pages
- `/` - Dashboard showing net balance and active groups
- `/groups` - List of all groups
- `/group/[id]` - Group details with expenses, balances, and activity log

**State Management:**
- Used React hooks (`useState`, `useEffect`) for local state
- Implemented loading states for better UX
- Error handling with user-friendly messages
- Automatic data refresh after mutations

**API Integration:**
- All API calls go through Next.js API routes (proxy pattern)
- This provides a layer of abstraction and allows for future middleware (auth, rate limiting, etc.)
- Example: `/api/add_expense/route.ts` forwards requests to Flask backend

**UI/UX Features:**
- Dark mode design with emerald green accents
- Responsive layout that works on mobile and desktop
- Smooth animations and transitions
- Loading spinners during API calls
- Success/error toast notifications"**

---

### **[6] KEY ALGORITHM - DEBT SIMPLIFICATION (1.5 minutes)**

**"Now, let me explain the most interesting part of this project - the debt simplification algorithm. This is what sets SplitVault apart.**

**The Problem:**
- In a group, people might owe each other money in complex ways
- For example, Alice owes Bob $50, Bob owes Charlie $30, and Charlie owes Alice $20
- Without simplification, that's 3 separate transactions
- But mathematically, we can reduce this to fewer transactions while preserving everyone's net balance

**My Solution - Net Balance Settlement Algorithm:**

**Step 1: Calculate Net Balances**
- For each person, sum up all the money they owe (negative) and all the money owed to them (positive)
- Example: If Alice owes $100 total but is owed $80, her net balance is -$20

**Step 2: Separate Debtors and Creditors**
- Debtors: People with negative net balance (they owe money overall)
- Creditors: People with positive net balance (they are owed money overall)
- Sort both lists by amount in descending order for optimal matching

**Step 3: Greedy Matching**
- Use a two-pointer approach
- Match the largest debtor with the largest creditor
- Transfer the minimum of the two amounts
- Update remaining balances
- Move to the next debtor or creditor when one is fully settled

**Step 4: Database Operations**
- Delete all old PENDING edges
- Insert new simplified edges
- Update the group's edges array
- Log the activity with reduction statistics

**Time Complexity:** O(n log n) due to sorting  
**Space Complexity:** O(n) for storing balances

**Example:**
```
Before Simplification (12 transactions):
Alice → Bob: $50
Alice → Charlie: $30
Bob → Charlie: $20
Charlie → Alice: $40
... (8 more)

After Simplification (5 transactions):
Alice → Bob: $30
Alice → Charlie: $10
... (3 more)

Reduction: 58%
```

**Mathematical Guarantee:**
- The algorithm preserves net balances exactly
- If Alice's net balance was -$20 before, it's -$20 after
- This is mathematically proven because we're just reorganizing the same total debts

**Implementation Details:**
- Only the group creator can trigger simplification (authorization check)
- The algorithm handles edge cases like zero balances and rounding errors (using 0.01 threshold)
- Activity log records the reduction percentage for transparency"**

---

### **[7] CHALLENGES FACED (1 minute)**

**"During development, I encountered several interesting challenges:**

**Challenge 1: Balance Calculation Edge Cases**
- **Problem:** When a user had multiple debts to the same person from different expenses, the balance calculation was aggregating them incorrectly
- **Solution:** I redesigned the `/groups/balances` endpoint to return individual edges with their IDs, not aggregated sums. This allows users to see exactly which expense created which debt and enables settling specific debts

**Challenge 2: Partial Settlement Logic**
- **Problem:** When a user made a partial payment, the system needed to update the edge amount, but also handle cases where the remaining amount was very small (like $0.01 due to rounding)
- **Solution:** Implemented a threshold check - if the remaining amount is less than $0.01, treat it as fully settled and delete the edge

**Challenge 3: Simplification Authorization**
- **Problem:** If any user could simplify debts, it could cause confusion and trust issues
- **Solution:** Added authorization logic so only the group creator can simplify debts. This makes sense because the creator is typically the organizer who has everyone's trust

**Challenge 4: Data Consistency**
- **Problem:** When adding an expense, multiple database operations were needed (insert expense, create edges, update group). If one failed, data could be inconsistent
- **Solution:** While MongoDB doesn't support multi-document transactions in all configurations, I ensured proper error handling and rollback logic. In a production environment, I would implement MongoDB transactions or use a two-phase commit pattern

**Challenge 5: Frontend-Backend Type Safety**
- **Problem:** TypeScript on frontend, Python on backend - no shared types
- **Solution:** Created TypeScript interfaces that mirror the backend data models. For a production app, I would generate these automatically using tools like OpenAPI/Swagger

**These challenges taught me a lot about real-world software development, edge case handling, and the importance of thorough testing."**

---

### **[8] CLOSING & FUTURE SCOPE (30 seconds)**

**"To summarize, SplitVault is a production-ready expense splitting application that demonstrates:**
- Full-stack development skills (Next.js, Flask, MongoDB)
- Algorithm design and implementation
- Database design and optimization
- Security best practices
- Problem-solving and debugging

**Future enhancements I'm planning:**
- Real-time updates using WebSockets
- Payment gateway integration (Stripe)
- Mobile app using React Native
- Email notifications for settlements
- Advanced analytics with charts
- Multi-currency support

**The entire codebase is well-documented, follows best practices, and is available on my GitHub. I'm proud of this project and I'm excited to discuss any aspect of it in more detail.**

**Thank you for your time. Do you have any questions?"**

---

## 📊 QUICK REFERENCE STATS

**Project Metrics:**
- **Total Lines of Code:** ~5,000+
- **Backend Endpoints:** 13
- **Database Collections:** 7
- **Frontend Components:** 10+
- **Development Time:** 3-4 weeks
- **Technologies Used:** 8 (Next.js, TypeScript, Tailwind, Flask, Python, MongoDB, PyMongo, Werkzeug)

**Technical Highlights:**
- ✅ Full-stack application
- ✅ RESTful API design
- ✅ Graph algorithm implementation
- ✅ NoSQL database design
- ✅ Secure authentication
- ✅ Responsive UI
- ✅ Real-time calculations
- ✅ Complete audit trail

---

## 🎯 KEY TALKING POINTS TO EMPHASIZE

1. **Algorithm Complexity:** The debt simplification algorithm is O(n log n), which is efficient even for large groups
2. **Scalability:** The architecture can handle thousands of users and groups with proper indexing
3. **Security:** Bcrypt hashing, input validation, authorization checks
4. **User Experience:** Real-time updates, loading states, error handling
5. **Code Quality:** Modular design, type safety, documentation
6. **Problem Solving:** Handled complex edge cases and data consistency issues

---

## 💡 ANTICIPATED QUESTIONS & ANSWERS

### Q: "Why did you choose MongoDB over a relational database?"

**A:** "Great question! I chose MongoDB for several reasons:

1. **Flexible Schema:** Expense participants can have different structures based on split type (equal, exact, percent). In SQL, this would require complex joins or JSON columns.

2. **Document Model:** Groups naturally contain arrays of members and expenses, which maps well to MongoDB's document structure.

3. **Scalability:** MongoDB Atlas provides easy horizontal scaling, which is important for a multi-tenant application.

4. **Development Speed:** The schema-less nature allowed me to iterate quickly during development.

However, I'm aware of the tradeoffs. For financial data, a relational database with ACID transactions would provide stronger consistency guarantees. In a production environment, I would consider using PostgreSQL with JSONB columns to get the best of both worlds."

---

### Q: "How would you handle concurrent updates to the same group?"

**A:** "Excellent question about concurrency! Currently, the application handles concurrent updates at the database level:

1. **MongoDB Atomic Operations:** I use atomic operations like `$push` and `$pull` which are thread-safe.

2. **Optimistic Locking:** For critical operations, I would implement version numbers on documents and check them before updates.

3. **Idempotency:** Settlement operations are designed to be idempotent - running them twice produces the same result.

For a production system, I would add:
- **Redis for distributed locking** when performing multi-step operations
- **Event sourcing** to track all state changes
- **WebSocket notifications** to alert users of concurrent changes
- **Conflict resolution UI** to let users resolve conflicts manually if needed"

---

### Q: "What about testing? Did you write tests?"

**A:** "That's an important question. Currently, the project has manual testing coverage, but I recognize the importance of automated testing. Here's my testing strategy:

**Current State:**
- Manual testing checklist covering all features
- Postman collection for API testing
- Browser testing across Chrome, Firefox, Safari

**Planned Testing:**
- **Unit Tests:** Using pytest for backend (testing individual functions like balance calculation)
- **Integration Tests:** Testing API endpoints with a test database
- **Frontend Tests:** Using Jest and React Testing Library
- **E2E Tests:** Using Playwright to test complete user flows

I would prioritize testing the debt simplification algorithm first, as it's the most complex and critical component. I've already validated it manually with various scenarios, but automated tests would provide regression protection."

---

### Q: "How would you deploy this application?"

**A:** "I've designed the application to be deployment-ready. Here's my deployment strategy:

**Current Setup:**
- Backend has `vercel.json` for Vercel deployment
- Frontend is Next.js, which deploys seamlessly to Vercel
- MongoDB Atlas is already cloud-hosted

**Deployment Steps:**
1. **Frontend:** Deploy to Vercel (automatic from GitHub)
2. **Backend:** Deploy Flask to Vercel Serverless Functions or Railway
3. **Database:** Already on MongoDB Atlas
4. **Environment Variables:** Configure in deployment platform

**Production Enhancements:**
- **Docker:** Containerize both frontend and backend
- **CI/CD:** GitHub Actions for automated testing and deployment
- **Monitoring:** Sentry for error tracking, Datadog for performance
- **CDN:** CloudFlare for static assets
- **Rate Limiting:** Implement API rate limiting
- **Caching:** Redis for frequently accessed data

The application is already structured to support this deployment architecture."

---

### Q: "What was the most difficult part of this project?"

**A:** "The most challenging aspect was designing the debt simplification algorithm to handle all edge cases correctly. Specifically:

1. **Circular Debts:** When A owes B, B owes C, and C owes A - the algorithm needed to detect and resolve these cycles.

2. **Floating Point Precision:** Money calculations with floating point numbers can introduce rounding errors. I had to implement careful rounding (to 2 decimal places) and threshold checks (0.01) to handle this.

3. **Preserving Net Balances:** The algorithm had to mathematically guarantee that everyone's net balance remained exactly the same after simplification. I validated this by calculating net balances before and after, and adding assertions.

4. **Database Consistency:** Simplification involves deleting old edges and creating new ones. I had to ensure this happened atomically to prevent data corruption.

I solved these by:
- Extensive manual testing with complex scenarios
- Adding detailed logging to track the algorithm's steps
- Implementing validation checks before and after simplification
- Creating comprehensive documentation of the algorithm

This challenge taught me the importance of algorithm correctness, especially when dealing with financial data."

---

## 🎬 DELIVERY TIPS

1. **Pace Yourself:** Speak clearly and not too fast. Pause between sections.
2. **Show Enthusiasm:** Demonstrate passion for the project
3. **Use Examples:** Refer to specific code or scenarios when explaining
4. **Be Honest:** If you don't know something, say so and explain how you'd find out
5. **Engage:** Make eye contact, watch for reactions, adjust based on interest
6. **Have Code Ready:** Be prepared to show specific files if asked
7. **Practice:** Rehearse this script 2-3 times before the interview

---

## ⏱️ TIMING BREAKDOWN

| Section | Duration | Cumulative |
|---------|----------|------------|
| Introduction | 1:00 | 1:00 |
| Project Overview | 1:30 | 2:30 |
| Technical Architecture | 2:00 | 4:30 |
| Backend Deep Dive | 2:00 | 6:30 |
| Frontend Implementation | 1:30 | 8:00 |
| Key Algorithm | 1:30 | 9:30 |
| Challenges Faced | 1:00 | 10:30 |
| Closing | 0:30 | 11:00 |

**Total: ~10-11 minutes** (with buffer for natural pauses)

---

## 🚀 GOOD LUCK!

**Remember:**
- You built something impressive
- You understand it deeply
- You can explain it clearly
- You're ready for this interview

**You've got this! 💪**

---

**Made by:** Aayush J. Gote  
**Date:** December 29, 2024  
**Project:** SplitVault Interview Preparation
