// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./IMNEE.sol"; // Import shared file

contract TaskEscrow {
    address public immutable MNEE_TOKEN;
    address public arbiter;

    enum TaskState { Created, Completed, Disputed, Released, Refunded }

    struct Task {
        address employer;
        address worker;
        uint256 amount;
        TaskState state;
        uint256 completedAt;
    }

    mapping(uint256 => Task) public tasks;
    uint256 public taskCount;
    
    uint256 public constant DISPUTE_WINDOW = 1 days;

    event TaskCreated(uint256 indexed taskId, address employer, address worker, uint256 amount);
    event TaskCompleted(uint256 indexed taskId, uint256 timestamp);
    event TaskDisputed(uint256 indexed taskId);
    event FundsReleased(uint256 indexed taskId, address to);

    constructor(address _mneeToken) {
        MNEE_TOKEN = _mneeToken;
        arbiter = msg.sender;
    }

    function createTask(address _worker, uint256 _amount) external returns (uint256) {
        require(_amount > 0, "Amount > 0");
        // Use IMNEE interface
        IMNEE(MNEE_TOKEN).transferFrom(msg.sender, address(this), _amount);

        taskCount++;
        tasks[taskCount] = Task({
            employer: msg.sender,
            worker: _worker,
            amount: _amount,
            state: TaskState.Created,
            completedAt: 0
        });

        emit TaskCreated(taskCount, msg.sender, _worker, _amount);
        return taskCount;
    }

    function completeTask(uint256 _taskId) external {
        Task storage t = tasks[_taskId];
        require(msg.sender == t.worker, "Only worker");
        require(t.state == TaskState.Created, "Invalid state");

        t.state = TaskState.Completed;
        t.completedAt = block.timestamp; 
        
        emit TaskCompleted(_taskId, block.timestamp);
    }

    function disputeTask(uint256 _taskId) external {
        Task storage t = tasks[_taskId];
        require(msg.sender == t.employer, "Only employer");
        require(t.state == TaskState.Completed, "Too late or too early");
        require(block.timestamp < t.completedAt + DISPUTE_WINDOW, "Dispute window closed");

        t.state = TaskState.Disputed;
        emit TaskDisputed(_taskId);
    }

    function withdraw(uint256 _taskId) external {
        Task storage t = tasks[_taskId];
        require(t.state == TaskState.Completed, "Invalid state");
        require(block.timestamp >= t.completedAt + DISPUTE_WINDOW, "Wait for dispute window");

        t.state = TaskState.Released;
        IMNEE(MNEE_TOKEN).transfer(t.worker, t.amount);
        
        emit FundsReleased(_taskId, t.worker);
    }

    function resolveDispute(uint256 _taskId, bool payWorker) external {
        require(msg.sender == arbiter, "Only arbiter");
        Task storage t = tasks[_taskId];
        require(t.state == TaskState.Disputed, "Not disputed");

        if (payWorker) {
            t.state = TaskState.Released;
            IMNEE(MNEE_TOKEN).transfer(t.worker, t.amount);
        } else {
            t.state = TaskState.Refunded;
            IMNEE(MNEE_TOKEN).transfer(t.employer, t.amount);
        }
    }
}