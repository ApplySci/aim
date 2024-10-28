// New file: optimizer.worker.js
importScripts('stats.js', 'optimizer.js');

self.onmessage = function(e) {
    const { seats, fixedRounds, omitPlayers, substitutes, timeLimit } = e.data;
    
    // Use 1 second for simple substitutions, otherwise use selected time
    const effectiveTimeLimit = omitPlayers.length < 4 ? 1 : (timeLimit || 30);
    
    const optimizer = new SeatingOptimizer(
        seats, 
        fixedRounds, 
        omitPlayers, 
        substitutes,
        effectiveTimeLimit
    );
    
    optimizer.setProgressCallback(message => {
        self.postMessage({ type: 'progress', message });
    });
    
    const result = optimizer.optimize();
    self.postMessage({ type: 'result', seating: result });
};
