// Function for generating random numbers
function getRandomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1) + min);
}

// Resource class
class Resource {
    constructor(id) {
        this.id = id;
        this.user = null;
        this.timeLeft = 0;
        this.waitingQueue = [];
    }

    // Assign user to resource using FIFO approach
    assignUser(user, time) {
        if (this.user === null) {
            this.user = user;
            this.timeLeft = time;
            console.log(`Resource ${this.id} is now being used by ${user.name} for ${time} seconds.`);
        } else {
            this.waitingQueue.push({ user, time });
            console.log(`${user.name} is added to the waiting list for Resource ${this.id}.`);
            this.displayWaitingUsers();
        }
    }

    // Process resource time with time progression
    processResource() {
        if (this.user !== null) {
            this.timeLeft--;
            if (this.timeLeft <= 0) {
                console.log(`Resource ${this.id} is now free. ${this.user.name} has finished.`);
                this.user = null;
                if (this.waitingQueue.length > 0) {
                    let nextUser = this.waitingQueue.shift(); // FIFO approach
                    console.log(`${nextUser.user.name} is now using Resource ${this.id}.`);
                    this.assignUser(nextUser.user, nextUser.time);
                }
            }
        }
    }

    // Display status of the resource
    displayStatus() {
        if (this.user !== null) {
            console.log(`Resource ${this.id} is currently used by ${this.user.name}, ${this.timeLeft}s left.`);
        } else {
            console.log(`Resource ${this.id} is free.`);
        }
        this.displayWaitingUsers();
    }

    // Display waiting users
    displayWaitingUsers() {
        if (this.waitingQueue.length > 0) {
            console.log(`Users waiting for Resource ${this.id}: ${this.waitingQueue.map(entry => entry.user.name).join(', ')}`);
        }
    }
}

// User class
class User {
    constructor(name) {
        this.name = name;
        this.assignedResource = null;
    }

    // Request a resource, ensuring users do not share the same resource simultaneously
    requestResource(resourceList) {
        const resourceIndex = getRandomInt(0, resourceList.length - 1);
        const timeRequired = getRandomInt(1, 30);
        let selectedResource = resourceList[resourceIndex];
        this.assignedResource = selectedResource;
        selectedResource.assignUser(this, timeRequired);
    }
}

// Simulation function
function simulate() {
    const numResources = 5; // Fixed to ensure waiting users
    const numUsers = 10; // More users than resources to create waiting scenarios
    const resources = [];
    const users = [];

    // Create resources
    for (let i = 0; i < numResources; i++) {
        resources.push(new Resource(i + 1));
    }

    // Create users
    for (let i = 0; i < numUsers; i++) {
        const user = new User(`User ${i + 1}`);
        users.push(user);
    }

    // Assign resources to users
    users.forEach(user => user.requestResource(resources));

    let simulationTime = 0;
    const simulationInterval = setInterval(() => {
        console.log(`\nSimulation Time: ${simulationTime}s`);
        resources.forEach(resource => resource.displayStatus());
        resources.forEach(resource => resource.processResource());
        
        // Stop simulation when all resources are free and queues are empty
        if (resources.every(resource => resource.user === null && resource.waitingQueue.length === 0)) {
            console.log("\nAll resources are free. Simulation complete.");
            clearInterval(simulationInterval);
        }
        
        simulationTime++;
    }, 1000);
}

// Run simulation
simulate();
