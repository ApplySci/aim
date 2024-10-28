class SeatingOptimizer {
    constructor(seats, fixedRounds, omitPlayers, substitutes) {
        this.seats = seats;
        this.fixedRounds = fixedRounds;
        this.omitPlayers = omitPlayers;
        this.substitutes = substitutes;
        this.onProgress = null;
        this.timeLimit = 15; // seconds
        this.populationSize = 50;
        this.statsCache = new Map();
        
        // Calculate baseline score from current seating
        this.baselineScore = this.scoreSolution(seats);
        this.targetScore = 0; // this.baselineScore + 10;
        
        const roundsToOptimize = seats.length - fixedRounds;
        const playersToReassign = omitPlayers.length - (omitPlayers.length % 4);
        
        this.log(`Using population size: ${this.populationSize}`);
    }

    setProgressCallback(callback) {
        this.onProgress = callback;
    }

    log(message) {
        if (this.onProgress) {
            this.onProgress(message);
        }
    }

    // Helper method to deep copy a seating arrangement
    deepCopySeats(seats) {
        return seats.map(round => 
            round.map(table => 
                [...table]
            )
        );
    }

    createSolution(seats, gaps, genome) {
        const hanchanCount = seats.length;
        seats = this.deepCopySeats(seats);

        for (let r = 0; r < hanchanCount; r++) {
            if (genome[r].breakups.length === 0) continue;

            let reseat = [];
            for (const breakup of genome[r].breakups) {
                for (let s = 0; s < 4; s++) {
                    const p = seats[r][breakup][s];
                    if (p === 0) {
                        // Remove this from gaps
                        gaps[r] = gaps[r].filter(([t1, s1]) => !(t1 === breakup && s1 === s));
                    } else {
                        reseat.push(p);
                        seats[r][breakup][s] = 0;
                    }
                }
            }

            const orderedReseat = genome[r].order
                .filter(i => i < reseat.length)
                .map(i => reseat[i]);

            for (let g = 0; g < gaps[r].length; g++) {
                const [t, s] = gaps[r][g];
                seats[r][t][s] = orderedReseat[g];
            }
        }

        return seats;
    }

    scoreSolution(seats, playersToIgnore = []) {
        // Create cache key from seating arrangement
        const cacheKey = seats.flat(3).join(',') + '|' + playersToIgnore.join(',');
        if (this.statsCache.has(cacheKey)) {
            return this.statsCache.get(cacheKey);
        }

        const stats = makeStats(seats, playersToIgnore);
        const hanchanCount = seats.length;
        const tableCount = seats[0].length;

        // Calculate penalties
        let score = stats.repeat3 * 30 + stats.repeat4 * 300;

        // Meets penalties
        for (let i = 3; i < stats.meets.length; i++) {
            score += 2 * stats.meets[i] * Math.pow(i - 1, 2);
        }

        // Wind penalties
        const windsMin = Math.floor(hanchanCount / 4);
        const windsMax = Math.floor((hanchanCount + 3) / 4);
        
        for (let i = 0; i < windsMin - 1; i++) {
            score += stats.wind[i] * Math.pow(2, windsMin - i);
        }
        for (let i = windsMax + 1; i < stats.wind.length; i++) {
            score += stats.wind[i] * Math.pow(2, i - windsMax);
        }

        // Table penalties
        const tableMax = Math.floor((tableCount + hanchanCount - 1) / tableCount);
        for (let i = tableMax + 1; i < stats.tables.length; i++) {
            score += stats.tables[i] * Math.pow(2, i - tableMax);
        }

        this.statsCache.set(cacheKey, score);
        return score;
    }

    randomGenome(seats, gaps) {
        const hanchanCount = seats.length;
        const genome = Array(hanchanCount).fill().map(() => ({
            order: [],
            breakups: []
        }));

        for (let r = 0; r < hanchanCount; r++) {
            const gapsToFill = gaps[r].length;
            const order = Array.from({length: gapsToFill}, (_, i) => i);
            // Shuffle order
            for (let i = order.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [order[i], order[j]] = [order[j], order[i]];
            }
            genome[r].order = order;
            genome[r].breakups = [];

            let remainingGaps = gapsToFill;
            while (remainingGaps > 0) {
                const breakup = Math.floor(Math.random() * seats[r].length);
                if (genome[r].breakups.includes(breakup)) continue;
                genome[r].breakups.push(breakup);
                remainingGaps -= 4;
            }
        }

        return genome;
    }

    crossover(genome1, genome2) {
        return genome1.map((g1, i) => {
            if (Math.random() < 0.5) {
                return { ...g1 };
            } else {
                return { ...genome2[i] };
            }
        });
    }

    mutate(genome, seats) {
        return genome.map(g => {
            if (Math.random() < 0.1) {
                // Mutate order
                const i = Math.floor(Math.random() * g.order.length);
                const j = Math.floor(Math.random() * g.order.length);
                const newOrder = [...g.order];
                [newOrder[i], newOrder[j]] = [newOrder[j], newOrder[i]];
                return { ...g, order: newOrder };
            }
            return { ...g };
        });
    }

    optimize() {
        const startTime = Date.now();
        const endTime = startTime + (this.timeLimit * 1000);
        
        // Initial status report
        this.log("\nOptimization Status:");
        this.log(`• Current seating score: ${this.baselineScore}`);
        this.log(`• Players to substitute: ${this.omitPlayers.length}`);
        this.log(`• Population size: ${this.populationSize}`);
        this.log(`• Time limit: ${this.timeLimit} seconds`);
        this.log("\nStarting optimization...\n");

        // Initialize gaps array
        const gaps = Array(this.seats.length).fill().map(() => []);
        const directSubs = this.omitPlayers.length % 4;
        
        if (directSubs > this.substitutes.length) {
            throw new Error("Not enough substitutes to fill the gaps");
        }

        // Remove omitted players and create gaps
        const workingSeats = this.deepCopySeats(this.seats);
        for (let r = this.fixedRounds; r < workingSeats.length; r++) {
            for (let t = 0; t < workingSeats[r].length; t++) {
                for (let p = 0; p < this.omitPlayers.length; p++) {
                    const seatIdx = workingSeats[r][t].indexOf(this.omitPlayers[p]);
                    if (seatIdx !== -1) {
                        if (p < directSubs) {
                            workingSeats[r][t][seatIdx] = this.substitutes[p];
                        } else {
                            workingSeats[r][t][seatIdx] = 0;
                            gaps[r].push([t, seatIdx]);
                        }
                    }
                }
            }
        }

        // Initialize population
        let population = Array(this.populationSize).fill()
            .map(() => this.randomGenome(workingSeats, gaps));
        
        let bestScore = Infinity;
        let bestGenome = null;
        let generation = 0;
        let lastProgressUpdate = 0;

        while (Date.now() < endTime) {
            generation++;
            
            // Evaluate fitness
            const fitness = population.map(genome => {
                const solution = this.createSolution(
                    workingSeats,
                    gaps.map(g => [...g]),
                    genome
                );
                const score = this.scoreSolution(solution, this.substitutes.slice(0, directSubs));
                return { score, genome };
            }).sort((a, b) => a.score - b.score);

            if (fitness[0].score < bestScore) {
                bestScore = fitness[0].score;
                bestGenome = fitness[0].genome;
                
                
                if (bestScore <= this.targetScore) {
                    this.log("\nSuccess! Found solution within acceptable range.");
                    break;
                }
            }

            // Show periodic progress
            const now = Date.now();
            if (now - lastProgressUpdate > 5000) { // Update every 5 seconds
                const timeLeft = Math.round((endTime - now) / 1000);
                this.log(`\nGeneration ${generation}: Current best ${bestScore} (${timeLeft}s remaining)`, "\r");
                lastProgressUpdate = now;
            }

            // Create next generation
            const newPopulation = [fitness[0].genome];  // Keep best solution
            while (newPopulation.length < this.populationSize) {
                const parent1 = fitness[Math.floor(Math.random() * 10)].genome;
                const parent2 = fitness[Math.floor(Math.random() * 10)].genome;
                let child = this.crossover(parent1, parent2);
                if (Math.random() < 0.1) {
                    child = this.mutate(child, workingSeats);
                }
                newPopulation.push(child);
            }
            population = newPopulation;
        }

        // Final status report
        this.log("\n\nOptimization Complete");
        this.log("\n-------------------\n");
        this.log(`• Score before substitutions: ${this.baselineScore}`);
        this.log(`• Final score: ${bestScore}`);
        this.log(`• Generations: ${generation}`);
        
        // Report termination reason
        if (Date.now() >= endTime) {
            this.log(`• Terminated: Time limit (${this.timeLimit}s) reached`);
        } else if (bestScore <= this.targetScore) {
            this.log(`• Terminated: Found solution better than target (${this.targetScore})`);
        } else if (bestScore === 0) {
            this.log(`• Terminated: Found perfect solution`);
        }

        const timeSpent = ((Date.now() - startTime) / 1000).toFixed(1);
        this.log(`• Time spent: ${timeSpent} seconds`);
        this.log("\n-------------------\n");
        
        return this.createSolution(workingSeats, gaps.map(g => [...g]), bestGenome);
    }

    // Helper method to format numbers consistently
    formatNumber(num) {
        return num.toLocaleString(undefined, { 
            minimumFractionDigits: 1, 
            maximumFractionDigits: 1 
        });
    }
}
