// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
    function transfer(address recipient, uint256 amount) external returns (bool);
}

contract TaskEscrow {
    // The Official MNEE Token Address
    address public immutable MNEE_TOKEN;

    enum TaskState { Created, Completed, Disputed, Released }

    struct Task {
        address employer;
        address worker;
        uint256 amount;
        TaskState state;
        uint256 createdAt;
        uint256 completedAt;
    }

    // Task ID -> Task Data
    mapping(uint256 => Task) public tasks;
    uint256 public taskCount;

    event TaskCreated(uint256 indexed taskId, address employer, address worker, uint256 amount);
    event TaskCompleted(uint256 indexed taskId);
    event FundsReleased(uint256 indexed taskId, address worker, uint256 amount);

    constructor(address _mneeToken) {
        MNEE_TOKEN = _mneeToken;
    }

    // 1. Employer locks money for a specific worker
    function createTask(address _worker, uint256 _amount) external returns (uint256) {
        require(_worker != address(0), "Invalid worker");
        require(_amount > 0, "Amount must be > 0");

        // Pull MNEE from Employer to this Vault
        // (Employer must approve this contract first!)
        bool success = IERC20(MNEE_TOKEN).transferFrom(msg.sender, address(this), _amount);
        require(success, "Transfer failed");

        taskCount++;
        tasks[taskCount] = Task({
            employer: msg.sender,
            worker: _worker,
            amount: _amount,
            state: TaskState.Created,
            createdAt: block.timestamp,
            completedAt: 0
        });

        emit TaskCreated(taskCount, msg.sender, _worker, _amount);
        return taskCount;
    }

    // 2. Worker signals "I am done"
    function completeTask(uint256 _taskId) external {
        Task storage t = tasks[_taskId];
        require(msg.sender == t.worker, "Only worker can complete");
        require(t.state == TaskState.Created, "Invalid state");

        t.state = TaskState.Completed;
        t.completedAt = block.timestamp;
        
        emit TaskCompleted(_taskId);
    }

    // 3. Release funds (For now, anyone can call this if it's "Completed")
    // Note: Day 5 will make this "Optimistic" (time-based)
    function releaseFunds(uint256 _taskId) external {
        Task storage t = tasks[_taskId];
        require(t.state == TaskState.Completed, "Work not done yet");
        
        t.state = TaskState.Released;
        
        bool success = IERC20(MNEE_TOKEN).transfer(t.worker, t.amount);
        require(success, "Release failed");
        
        emit FundsReleased(_taskId, t.worker, t.amount);
    }
}