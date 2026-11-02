from sqlalchemy.orm import Session
from app.models.practice import QuestionBank

COMPREHENSIVE_QUESTIONS = [
    # 1. Data Structures and Algorithms
    {
        "subject": "Data Structures and Algorithms",
        "category": "DSA",
        "difficulty": "Intermediate",
        "role_track": "Software Development Engineer",
        "programming_language": "Python",
        "question_type": "Coding",
        "title": "Two Sum Problem",
        "question_text": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume each input has exactly one solution, and you may not use the same element twice. Aim for O(n) time complexity.",
        "expected_keywords": ["hash map", "dictionary", "O(n)", "complement", "indices"],
        "sample_answer": "Use a hash map to store each number and its index. For each number, compute complement = target - num. If complement is in the map, return [map[complement], current_index]. Otherwise, insert num: current_index.",
        "hints": ["Think about trading space for time using a hash table to achieve O(n) lookup.", "What is the complement you need for each number?"],
        "options": [],
        "correct_option_index": None,
        "explanation": "A hash map allows O(1) average-time lookups for the needed complement (target - x), yielding overall O(n) time and O(n) space complexity.",
        "code_template": "def solution(nums, target):\n    # Write your solution here\n    # Return a list of two indices [i, j]\n    seen = {}\n    for i, num in enumerate(nums):\n        diff = target - num\n        if diff in seen:\n            return [seen[diff], i]\n        seen[num] = i\n    return []\n",
        "test_cases": [
            {"input": "[[2, 7, 11, 15], 9]", "expected_output": "[0, 1]", "hidden": False},
            {"input": "[[3, 2, 4], 6]", "expected_output": "[1, 2]", "hidden": False},
            {"input": "[[3, 3], 6]", "expected_output": "[0, 1]", "hidden": True}
        ],
        "source_type": "curated_educational",
        "source_name": "GeeksforGeeks Educational Standards",
        "source_url": "https://www.geeksforgeeks.org/check-if-pair-with-given-sum-exists-in-array/"
    },
    {
        "subject": "Data Structures and Algorithms",
        "category": "DSA",
        "difficulty": "Beginner",
        "role_track": "Software Development Engineer",
        "programming_language": "Python",
        "question_type": "MCQ",
        "title": "Time Complexity of Binary Search",
        "question_text": "What is the worst-case time complexity of standard Binary Search on a sorted array of n elements?",
        "expected_keywords": ["O(log n)", "divide and conquer", "halving search space"],
        "sample_answer": "O(log n)",
        "hints": ["Each comparison cuts the search space in half."],
        "options": ["O(n)", "O(log n)", "O(n log n)", "O(1)"],
        "correct_option_index": 1,
        "explanation": "Binary search divides the search interval in half at each iteration, resulting in at most log2(n) comparisons, which is O(log n).",
        "code_template": "",
        "test_cases": [],
        "source_type": "curated_educational",
        "source_name": "Official Educational Standard",
        "source_url": "https://en.wikipedia.org/wiki/Binary_search_algorithm"
    },
    {
        "subject": "Data Structures and Algorithms",
        "category": "DSA",
        "difficulty": "Advanced",
        "role_track": "Software Development Engineer",
        "programming_language": "Python",
        "question_type": "Theory",
        "title": "Dijkstra's vs Bellman-Ford Shortest Path",
        "question_text": "Compare Dijkstra's algorithm and the Bellman-Ford algorithm for finding shortest paths in weighted graphs. When must you use Bellman-Ford instead of Dijkstra?",
        "expected_keywords": ["negative edge weights", "negative cycles", "priority queue", "relaxation", "O(V + E log V)", "O(V * E)"],
        "sample_answer": "Dijkstra's algorithm uses a greedy approach with a min-priority queue and achieves O((V + E) log V) time, but it assumes all edge weights are non-negative. If any edge weights are negative, Dijkstra's may produce incorrect results. Bellman-Ford relaxes all edges V-1 times and runs in O(V * E), safely supporting negative edge weights and detecting negative weight cycles.",
        "hints": ["Consider how greedy choices behave with negative edge weights.", "Mention cycle detection."],
        "options": [],
        "correct_option_index": None,
        "explanation": "Bellman-Ford is necessary whenever negative edge weights exist or negative cycles must be detected, whereas Dijkstra is preferred for performance on strictly non-negative graphs.",
        "code_template": "",
        "test_cases": [],
        "source_type": "curated_educational",
        "source_name": "MIT OpenCourseWare Algorithms",
        "source_url": "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/"
    },

    # 2. Java
    {
        "subject": "Java",
        "category": "Backend",
        "difficulty": "Intermediate",
        "role_track": "Java Developer",
        "programming_language": "Java",
        "question_type": "MCQ",
        "title": "Java Memory Model - String Constant Pool",
        "question_text": "Where is the String Constant Pool stored in modern Java (Java 8 and above)?",
        "expected_keywords": ["Heap", "String Pool", "Metaspace", "PermGen"],
        "sample_answer": "In the Java Heap memory.",
        "hints": ["Java 7 moved it out of PermGen, and Java 8 replaced PermGen with Metaspace."],
        "options": ["In native Metaspace", "In the Java Heap memory", "In the Thread Stack memory", "In the JVM Method Area exclusively"],
        "correct_option_index": 1,
        "explanation": "Starting in Java 7 and continued through Java 8+, the String Constant Pool was moved from PermGen into the main Java Heap memory so it can be garbage collected like regular heap objects.",
        "code_template": "",
        "test_cases": [],
        "source_type": "curated_educational",
        "source_name": "Oracle Java SE Documentation",
        "source_url": "https://docs.oracle.com/en/java/javase/17/docs/api/"
    },
    {
        "subject": "Java",
        "category": "Backend",
        "difficulty": "Advanced",
        "role_track": "Java Developer",
        "programming_language": "Java",
        "question_type": "Theory",
        "title": "Java Garbage Collection: G1GC vs ZGC",
        "question_text": "Explain how the Garbage-First (G1) collector works compared to modern ultra-low-latency collectors like ZGC. How do they minimize Stop-The-World (STW) pause times?",
        "expected_keywords": ["Stop-The-World", "regions", "colored pointers", "load barriers", "concurrent marking", "pause times"],
        "sample_answer": "G1GC divides the heap into equal-sized regions and prioritizes collecting regions with the most garbage ('garbage-first'). It allows users to set a target max pause time (e.g. -XX:MaxGCPauseMillis). ZGC is a concurrent, scalable, low-latency garbage collector designed for heaps up to multiple terabytes. It uses colored pointers (metadata bits in 64-bit pointers) and load barriers to perform memory compaction concurrently with application threads, achieving sub-millisecond STW pause times.",
        "hints": ["Discuss regional heap partitioning vs contiguous generational heap.", "Mention colored pointers and load barriers."],
        "options": [],
        "correct_option_index": None,
        "explanation": "ZGC achieves predictable sub-millisecond pauses by shifting heavy compaction and relocation work into concurrent phases with load barriers.",
        "code_template": "",
        "test_cases": [],
        "source_type": "curated_educational",
        "source_name": "Oracle Java Virtual Machine Guide",
        "source_url": "https://docs.oracle.com/en/java/javase/17/gctuning/garbage-first-garbage-collector.html"
    },

    # 3. Python
    {
        "subject": "Python",
        "category": "Backend",
        "difficulty": "Intermediate",
        "role_track": "Python Developer",
        "programming_language": "Python",
        "question_type": "MCQ",
        "title": "Python Global Interpreter Lock (GIL)",
        "question_text": "What is the primary effect of CPython's Global Interpreter Lock (GIL) on multi-threaded programs?",
        "expected_keywords": ["GIL", "single thread", "CPU-bound", "bytecode"],
        "sample_answer": "It restricts execution of Python bytecode to a single native thread at a time.",
        "hints": ["Does the GIL prevent multi-threading for CPU-bound tasks or I/O-bound tasks?"],
        "options": [
            "It restricts execution of Python bytecode to a single native thread at a time",
            "It prevents threads from reading shared memory variables",
            "It automatically optimizes CPU-bound multi-threaded workloads across all cores",
            "It disables asynchronous I/O event loops"
        ],
        "correct_option_index": 0,
        "explanation": "The GIL is a mutex that protects access to Python objects, preventing multiple native threads from executing Python bytecode simultaneously. For CPU-bound tasks, multiprocessing or C-extensions are required to achieve true parallelism.",
        "code_template": "",
        "test_cases": [],
        "source_type": "curated_educational",
        "source_name": "Python Official Documentation",
        "source_url": "https://docs.python.org/3/c-api/init.html#thread-state-and-the-global-interpreter-lock"
    },
    {
        "subject": "Python",
        "category": "Backend",
        "difficulty": "Intermediate",
        "role_track": "Python Developer",
        "programming_language": "Python",
        "question_type": "Coding",
        "title": "Valid Parentheses Checker",
        "question_text": "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid. An input string is valid if open brackets are closed by the same type of brackets and in the correct order.",
        "expected_keywords": ["stack", "LIFO", "bracket matching", "O(n)"],
        "sample_answer": "Use a stack. Push open brackets. For close brackets, pop from the stack and verify it matches the corresponding opening bracket. The string is valid if the stack is empty at the end.",
        "hints": ["Use a stack to track unmatched opening brackets."],
        "options": [],
        "correct_option_index": None,
        "explanation": "A stack ensures that the most recently opened bracket is closed first, guaranteeing correct nesting in O(n) time.",
        "code_template": "def solution(s):\n    # Write your solution here\n    # Return True if valid, False otherwise\n    stack = []\n    mapping = {')': '(', '}': '{', ']': '['}\n    for char in s:\n        if char in mapping:\n            top = stack.pop() if stack else '#'\n            if mapping[char] != top:\n                return False\n        else:\n            stack.append(char)\n    return not stack\n",
        "test_cases": [
            {"input": "\"()[]{}\"", "expected_output": "True", "hidden": False},
            {"input": "\"(]\"", "expected_output": "False", "hidden": False},
            {"input": "\"([{}])\"", "expected_output": "True", "hidden": True}
        ],
        "source_type": "curated_educational",
        "source_name": "Official Educational Standard",
        "source_url": "https://docs.python.org/3/tutorial/datastructures.html#using-lists-as-stacks"
    },

    # 4. C++
    {
        "subject": "C++",
        "category": "Backend",
        "difficulty": "Advanced",
        "role_track": "Software Development Engineer",
        "programming_language": "C++",
        "question_type": "MCQ",
        "title": "C++ Smart Pointers and Ownership",
        "question_text": "Which smart pointer in modern C++ (C++11 and later) represents exclusive, non-copyable ownership of a dynamically allocated resource?",
        "expected_keywords": ["std::unique_ptr", "exclusive ownership", "move semantics"],
        "sample_answer": "std::unique_ptr",
        "hints": ["It cannot be copy-constructed, only moved."],
        "options": ["std::shared_ptr", "std::weak_ptr", "std::unique_ptr", "std::auto_ptr"],
        "correct_option_index": 2,
        "explanation": "std::unique_ptr enforces exclusive ownership; copy constructor and copy assignment operators are deleted, enabling safe RAII without reference counting overhead.",
        "code_template": "",
        "test_cases": [],
        "source_type": "curated_educational",
        "source_name": "cppreference C++ Standard Library",
        "source_url": "https://en.cppreference.com/w/cpp/memory/unique_ptr"
    },

    # 5. Operating Systems
    {
        "subject": "Operating Systems",
        "category": "System Design",
        "difficulty": "Intermediate",
        "role_track": "Backend Developer",
        "programming_language": "Python",
        "question_type": "MCQ",
        "title": "Deadlock Necessary Conditions",
        "question_text": "Which of the following is NOT one of the four Coffman conditions necessary for a deadlock to occur in an operating system?",
        "expected_keywords": ["Coffman conditions", "deadlock", "mutual exclusion", "hold and wait", "no preemption", "circular wait"],
        "sample_answer": "Paging and Segmentation",
        "hints": ["The four conditions are Mutual Exclusion, Hold and Wait, No Preemption, and Circular Wait."],
        "options": ["Mutual Exclusion", "Hold and Wait", "Paging and Segmentation", "Circular Wait"],
        "correct_option_index": 2,
        "explanation": "The 4 Coffman conditions for deadlock are: 1) Mutual Exclusion, 2) Hold and Wait, 3) No Preemption, and 4) Circular Wait. Paging and Segmentation are virtual memory management techniques.",
        "code_template": "",
        "test_cases": [],
        "source_type": "curated_educational",
        "source_name": "Operating Systems: Three Easy Pieces (OSTEP)",
        "source_url": "https://pages.cs.wisc.edu/~remzi/OSTEP/threads-bugs.pdf"
    },
    {
        "subject": "Operating Systems",
        "category": "System Design",
        "difficulty": "Advanced",
        "role_track": "Backend Developer",
        "programming_language": "Python",
        "question_type": "Theory",
        "title": "Virtual Memory and Page Fault Handling",
        "question_text": "Describe step-by-step what occurs in the hardware and operating system kernel when a user process generates a Page Fault during memory access.",
        "expected_keywords": ["MMU", "page table", "valid bit", "trap", "page fault handler", "swap/disk", "TLB", "context switch"],
        "sample_answer": "1. MMU looks up virtual address in TLB/page table and finds the valid bit is 0 (page not present in physical RAM). 2. CPU generates a hardware trap/page fault exception to OS kernel. 3. Kernel page fault handler saves process context. 4. Kernel checks if address is valid in process virtual address space (if invalid, raises SIGSEGV). 5. Kernel allocates a free physical frame (or evicts a victim page using LRU/Clock). 6. Kernel schedules I/O disk read to load the missing page into physical RAM. 7. Once loaded, kernel updates page table with physical frame and sets valid bit = 1. 8. Process context is restored and instruction is re-executed.",
        "hints": ["Start from the MMU address translation and end with re-executing the faulting instruction."],
        "options": [],
        "correct_option_index": None,
        "explanation": "Page fault handling bridges hardware MMU detection with OS swap disk I/O and page table synchronization.",
        "code_template": "",
        "test_cases": [],
        "source_type": "curated_educational",
        "source_name": "Operating Systems: Three Easy Pieces (OSTEP)",
        "source_url": "https://pages.cs.wisc.edu/~remzi/OSTEP/vm-paging.pdf"
    },

    # 6. DBMS
    {
        "subject": "DBMS",
        "category": "Backend",
        "difficulty": "Intermediate",
        "role_track": "Backend Developer",
        "programming_language": "SQL",
        "question_type": "MCQ",
        "title": "ACID Properties in Relational Databases",
        "question_text": "Which ACID property guarantees that all database updates within a transaction are completed successfully, or if a failure occurs, all changes are rolled back completely?",
        "expected_keywords": ["Atomicity", "Consistency", "Isolation", "Durability"],
        "sample_answer": "Atomicity",
        "hints": ["'All or nothing' property."],
        "options": ["Atomicity", "Consistency", "Isolation", "Durability"],
        "correct_option_index": 0,
        "explanation": "Atomicity ensures that a transaction is treated as a single, indivisible unit of work: either all operations succeed, or none do.",
        "code_template": "",
        "test_cases": [],
        "source_type": "curated_educational",
        "source_name": "PostgreSQL Documentation - Transactions",
        "source_url": "https://www.postgresql.org/docs/current/tutorial-transactions.html"
    },

    # 7. Computer Networks
    {
        "subject": "Computer Networks",
        "category": "System Design",
        "difficulty": "Intermediate",
        "role_track": "Full Stack Developer",
        "programming_language": "Python",
        "question_type": "MCQ",
        "title": "TCP Three-Way Handshake",
        "question_text": "What is the correct sequence of packets sent during the establishment of a standard TCP connection between a client and a server?",
        "expected_keywords": ["SYN", "SYN-ACK", "ACK", "handshake"],
        "sample_answer": "SYN -> SYN-ACK -> ACK",
        "hints": ["Client initiates with SYN."],
        "options": ["SYN -> ACK -> SYN-ACK", "SYN -> SYN-ACK -> ACK", "ACK -> SYN -> SYN-ACK", "FIN -> ACK -> FIN-ACK"],
        "correct_option_index": 1,
        "explanation": "The client sends a SYN packet, the server responds with SYN-ACK, and the client replies with ACK to establish a reliable bidirectional byte stream.",
        "code_template": "",
        "test_cases": [],
        "source_type": "curated_educational",
        "source_name": "IETF RFC 793 Transmission Control Protocol",
        "source_url": "https://datatracker.ietf.org/doc/html/rfc793"
    },

    # 8. Artificial Intelligence
    {
        "subject": "Artificial Intelligence",
        "category": "AI/ML",
        "difficulty": "Intermediate",
        "role_track": "AI/ML Engineer",
        "programming_language": "Python",
        "question_type": "MCQ",
        "title": "A* Search Algorithm Heuristic Admissibility",
        "question_text": "In the A* search algorithm, what does it mean for a heuristic function h(n) to be 'admissible'?",
        "expected_keywords": ["admissible", "never overestimates", "optimal", "shortest path"],
        "sample_answer": "It never overestimates the actual minimal cost to reach the goal.",
        "hints": ["h(n) <= h*(n) for all nodes n."],
        "options": [
            "It never overestimates the actual minimal cost to reach the goal",
            "It always returns 0 for all nodes",
            "It runs in strictly constant O(1) time",
            "It guarantees that the branching factor is reduced to 1"
        ],
        "correct_option_index": 0,
        "explanation": "An admissible heuristic never overestimates the true distance to the goal, which guarantees that A* tree search will find an optimal shortest path.",
        "code_template": "",
        "test_cases": [],
        "source_type": "curated_educational",
        "source_name": "Stanford CS221 Artificial Intelligence Principles",
        "source_url": "https://stanford.edu/~shervine/teaching/cs-229/"
    },

    # 9. Machine Learning
    {
        "subject": "Machine Learning",
        "category": "AI/ML",
        "difficulty": "Intermediate",
        "role_track": "AI/ML Engineer",
        "programming_language": "Python",
        "question_type": "MCQ",
        "title": "Precision vs Recall Trade-off",
        "question_text": "In a medical diagnostic system where missing a malignant tumor (false negative) is catastrophic, which metric should you maximize first?",
        "expected_keywords": ["Recall", "Sensitivity", "False Negatives", "Precision"],
        "sample_answer": "Recall (Sensitivity)",
        "hints": ["Recall = TP / (TP + FN)."],
        "options": ["Precision", "Recall (Sensitivity)", "Specificity", "Fidelity"],
        "correct_option_index": 1,
        "explanation": "Recall measures the proportion of actual positives that were correctly identified. Maximizing recall minimizes false negatives, ensuring life-threatening conditions are not missed.",
        "code_template": "",
        "test_cases": [],
        "source_type": "curated_educational",
        "source_name": "Scikit-Learn Model Evaluation Guide",
        "source_url": "https://scikit-learn.org/stable/modules/model_evaluation.html"
    },

    # 10. Deep Learning
    {
        "subject": "Deep Learning",
        "category": "AI/ML",
        "difficulty": "Advanced",
        "role_track": "AI/ML Engineer",
        "programming_language": "Python",
        "question_type": "Theory",
        "title": "Vanishing Gradients and Residual Connections",
        "question_text": "Why does the vanishing gradient problem occur in deep feedforward networks, and how do Residual Connections (ResNets: y = F(x) + x) solve it?",
        "expected_keywords": ["vanishing gradient", "chain rule", "backpropagation", "skip connection", "identity mapping", "gradient flow"],
        "sample_answer": "During backpropagation, gradients are multiplied layer-by-layer via the chain rule. When activation functions have derivatives < 1 (e.g. sigmoid or tanh), gradients shrink exponentially with depth, causing early layers to train very slowly or stall. Residual connections introduce an identity shortcut y = F(x) + x. When computing dy/dx = dF/dx + 1, the '+ 1' ensures gradients can flow directly back through layers without vanishing.",
        "hints": ["Think about the derivative of the identity term in backpropagation."],
        "options": [],
        "correct_option_index": None,
        "explanation": "The additive identity connection guarantees a highway for gradient flow directly back to shallow layers.",
        "code_template": "",
        "test_cases": [],
        "source_type": "curated_educational",
        "source_name": "PyTorch Deep Learning Tutorials",
        "source_url": "https://pytorch.org/docs/stable/index.html"
    },

    # 11. SQL
    {
        "subject": "SQL",
        "category": "Backend",
        "difficulty": "Intermediate",
        "role_track": "Data Analyst",
        "programming_language": "SQL",
        "question_type": "Coding",
        "title": "Find Second Highest Salary",
        "question_text": "Write a SQL query to find the second highest distinct salary from an Employee table with columns (id, salary). If there is no second highest salary, return NULL.",
        "expected_keywords": ["SELECT", "DISTINCT", "ORDER BY", "DESC", "LIMIT", "OFFSET", "DENSE_RANK"],
        "sample_answer": "SELECT (SELECT DISTINCT salary FROM Employee ORDER BY salary DESC LIMIT 1 OFFSET 1) AS SecondHighestSalary;",
        "hints": ["Use DISTINCT to ignore ties, and LIMIT 1 OFFSET 1 or DENSE_RANK."],
        "options": [],
        "correct_option_index": None,
        "explanation": "Selecting DISTINCT salary ordered descending with OFFSET 1 fetches the exact second unique salary.",
        "code_template": "SELECT MAX(salary) FROM Employee WHERE salary < (SELECT MAX(salary) FROM Employee);",
        "test_cases": [
            {
                "input": "Employee records: [1, 100], [2, 200], [3, 300]",
                "expected_output": "[[200]]",
                "setup_sql": "CREATE TABLE Employee (id INT, salary INT); INSERT INTO Employee VALUES (1, 100), (2, 200), (3, 300);",
                "hidden": False
            },
            {
                "input": "Employee with duplicate top salaries: [1, 500], [2, 500], [3, 300]",
                "expected_output": "[[300]]",
                "setup_sql": "CREATE TABLE Employee (id INT, salary INT); INSERT INTO Employee VALUES (1, 500), (2, 500), (3, 300);",
                "hidden": False
            }
        ],
        "source_type": "curated_educational",
        "source_name": "SQLite SQL Language Documentation",
        "source_url": "https://www.sqlite.org/lang_select.html"
    },

    # 12. System Design
    {
        "subject": "System Design",
        "category": "System Design",
        "difficulty": "Advanced",
        "role_track": "Full Stack Developer",
        "programming_language": "Python",
        "question_type": "Scenario",
        "title": "Scaling WebSocket Architecture for 1 Million Users",
        "question_text": "You are designing the real-time notification engine for an e-commerce platform during flash sales. The system must support 1,000,000 concurrent connected WebSocket users across multiple load-balanced nodes. How do you design connection state management and cross-node message routing?",
        "expected_keywords": ["Redis Pub/Sub", "sticky sessions", "socket servers", "load balancer", "horizontal scaling", "message broker", "Kafka", "backpressure"],
        "sample_answer": "1. Edge Layer: Reverse proxy (e.g. Nginx or AWS ALB) terminates TLS and performs WebSocket connection upgrades, load balancing across a stateless fleet of WebSocket gateway instances. 2. Routing & Pub/Sub: Since client A may be connected to Node 1 and notification originates from Node 5, back each gateway with Redis Pub/Sub or Kafka topics keyed by user/tenant ID. 3. Connection Registry: Keep an in-memory map on each node of active local socket IDs to user IDs. 4. Backpressure & Heartbeats: Implement ping/pong frames every 30s to prune dead connections and throttle broadcast floods.",
        "hints": ["How do different servers communicate when user A is on Server 1 and sender is on Server 2?"],
        "options": [],
        "correct_option_index": None,
        "explanation": "Decoupling persistent socket connections from business logic via a distributed Pub/Sub bus enables seamless horizontal scaling.",
        "code_template": "",
        "test_cases": [],
        "source_type": "curated_educational",
        "source_name": "System Design Primer",
        "source_url": "https://github.com/donnemartin/system-design-primer"
    },

    # 13. OOP
    {
        "subject": "OOP",
        "category": "Backend",
        "difficulty": "Beginner",
        "role_track": "Software Development Engineer",
        "programming_language": "Python",
        "question_type": "MCQ",
        "title": "Four Pillars of Object-Oriented Programming",
        "question_text": "Which of the following correctly lists the four foundational principles of Object-Oriented Programming (OOP)?",
        "expected_keywords": ["Encapsulation", "Abstraction", "Inheritance", "Polymorphism"],
        "sample_answer": "Encapsulation, Abstraction, Inheritance, Polymorphism",
        "hints": ["Think of the acronym EAIP."],
        "options": [
            "Encapsulation, Abstraction, Inheritance, Polymorphism",
            "Compilation, Interpretation, Memory, Concurrency",
            "Modularity, Recursion, Iteration, Pointers",
            "Classes, Instances, Modules, Packages"
        ],
        "correct_option_index": 0,
        "explanation": "The four pillars of OOP are Encapsulation (data hiding), Abstraction (hiding implementation complexity), Inheritance (code reuse), and Polymorphism (many forms/overriding).",
        "code_template": "",
        "test_cases": [],
        "source_type": "curated_educational",
        "source_name": "Oracle Java OOP Concepts Guide",
        "source_url": "https://docs.oracle.com/javase/tutorial/java/concepts/"
    },

    # 14. Computer Science Fundamentals
    {
        "subject": "Computer Science Fundamentals",
        "category": "DSA",
        "difficulty": "Intermediate",
        "role_track": "Software Development Engineer",
        "programming_language": "Python",
        "question_type": "MCQ",
        "title": "Endianness in Computer Architecture",
        "question_text": "In a Little-Endian computer architecture, how are multibyte integers stored in memory?",
        "expected_keywords": ["Little-Endian", "least significant byte", "lowest address"],
        "sample_answer": "The least significant byte is stored at the lowest memory address.",
        "hints": ["'Little end' comes first at the starting memory address."],
        "options": [
            "The least significant byte is stored at the lowest memory address",
            "The most significant byte is stored at the lowest memory address",
            "Bytes are stored in random hashed positions",
            "Only the sign bit is stored at the lowest address"
        ],
        "correct_option_index": 0,
        "explanation": "In Little-Endian architectures (such as x86 and modern ARM configurations), the least significant byte (LSB) is placed at the lowest numeric memory address.",
        "code_template": "",
        "test_cases": [],
        "source_type": "curated_educational",
        "source_name": "Computer Systems: A Programmer's Perspective (CS:APP)",
        "source_url": "https://en.wikipedia.org/wiki/Endianness"
    }
]

def seed_question_bank(db: Session):
    """
    Seeds comprehensive questions across all 14 required technical subjects,
    ensuring legitimate source URLs, test cases, and question types.
    """
    for q in COMPREHENSIVE_QUESTIONS:
        # Check if question with this title already exists
        exists = db.query(QuestionBank).filter(QuestionBank.title == q["title"]).first()
        if not exists:
            new_q = QuestionBank(
                category=q.get("category", "DSA"),
                subject=q.get("subject", "Computer Science Fundamentals"),
                difficulty=q.get("difficulty", "Intermediate"),
                role_track=q.get("role_track", "Software Development Engineer"),
                programming_language=q.get("programming_language", "Python"),
                question_type=q.get("question_type", "Theory"),
                title=q["title"],
                question_text=q["question_text"],
                expected_keywords=q.get("expected_keywords", []),
                sample_answer=q["sample_answer"],
                hints=q.get("hints", []),
                options=q.get("options", []),
                correct_option_index=q.get("correct_option_index"),
                explanation=q.get("explanation", ""),
                code_template=q.get("code_template", ""),
                test_cases=q.get("test_cases", []),
                source_type=q.get("source_type", "curated_educational"),
                source_name=q.get("source_name", "Official Educational Standard"),
                source_url=q.get("source_url")
            )
            db.add(new_q)
        else:
            # Update columns if they were null
            if not exists.subject or exists.subject == "Computer Science Fundamentals":
                exists.subject = q.get("subject", exists.subject)
            if not exists.options:
                exists.options = q.get("options", [])
            if exists.correct_option_index is None:
                exists.correct_option_index = q.get("correct_option_index")
            if not exists.explanation:
                exists.explanation = q.get("explanation", "")
            if not exists.test_cases:
                exists.test_cases = q.get("test_cases", [])
            if not exists.source_url:
                exists.source_url = q.get("source_url")
            if not exists.source_name:
                exists.source_name = q.get("source_name", "Official Educational Standard")

    db.commit()
