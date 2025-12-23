// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
}

contract TaskEscrow {
    struct Task {
        uint256 id;
        address client;
        address worker;
        uint256 amount;
        bool completed;
        string description;
        string output; // <--- NEW: Stores the Agent's response
    }

    IERC20 public token;
    uint256 public nextTaskId;
    mapping(uint256 => Task) public tasks;

    event TaskCreated(uint256 indexed taskId, address indexed client, address indexed worker, uint256 amount);
    // NEW: The event now includes the output so the frontend can see it instantly
    event TaskCompleted(uint256 indexed taskId, string output);

    constructor(address _tokenAddress) {
        token = IERC20(_tokenAddress);
    }

    function createTask(address _worker, uint256 _amount) external returns (uint256) {
        require(token.transferFrom(msg.sender, address(this), _amount), "Payment failed");
        uint256 taskId = nextTaskId++;
        // Initialize with empty output
        tasks[taskId] = Task(taskId, msg.sender, _worker, _amount, false, "Task", "");
        emit TaskCreated(taskId, msg.sender, _worker, _amount);
        return taskId;
    }

    // NEW: Accepts _output string
    function completeTask(uint256 _taskId, string memory _output) external {
        Task storage task = tasks[_taskId];
        require(!task.completed, "Already completed");
        require(msg.sender == task.worker, "Only worker can complete");

        task.completed = true;
        task.output = _output; // <--- Save the response on-chain
        
        require(token.transfer(task.worker, task.amount), "Transfer failed");
        emit TaskCompleted(_taskId, _output);
    }
}