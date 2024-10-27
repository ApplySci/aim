// New file: optimizer.worker.js
importScripts('stats.js', 'optimizer.js');

self.onmessage = function(e) {
    const { seats, fixedRounds, omitPlayers, substitutes } = e.data;
    
    const optimizer = new SeatingOptimizer(seats, fixedRounds, omitPlayers, substitutes);
    optimizer.setProgressCallback(message => {
        self.postMessage({ type: 'progress', message });
    });
    
    const result = optimizer.optimize();
    self.postMessage({ type: 'result', seating: result });
};
