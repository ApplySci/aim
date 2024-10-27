/**
 * Calculate statistics for a given seating arrangement
 * @param {number[][][]} seats - 3D array [hanchan][table][seat]
 * @param {number[]} ignorePlayers - List of player numbers to ignore
 * @returns {Object} Statistics object
 */
function makeStats(seats, ignorePlayers = []) {
    const tableCount = seats[0].length;
    const playerCount = Math.max(
        tableCount * 4,
        ...ignorePlayers
    );
    const hanchanCount = seats.length;

    // Initialize arrays
    const playerPairs = Array(playerCount + 1).fill().map(() => 
        Array(playerCount + 1).fill(0)
    );
    const indirectMeets = Array(playerCount + 1).fill().map(() => 
        Array(playerCount + 1).fill(0)
    );
    const playerTables = Array(playerCount + 1).fill().map(() => 
        Array(tableCount).fill(0)
    );
    const playerWinds = Array(playerCount + 1).fill().map(() => 
        Array(4).fill(0)
    );

    // Track 3-player and 4-player meets
    const meets3 = new Map();
    const meets4 = new Map();

    // Calculate direct meetings and wind/table frequencies
    for (let hanchan = 0; hanchan < hanchanCount; hanchan++) {
        for (let table = 0; table < tableCount; table++) {
            const playersAtTable = seats[hanchan][table];
            if (playersAtTable.every(p => p === 0)) continue;

            for (let seat1 = 0; seat1 < 4; seat1++) {
                const player1 = playersAtTable[seat1];
                playerTables[player1][table]++;
                playerWinds[player1][seat1]++;
                
                for (let seat2 = seat1 + 1; seat2 < 4; seat2++) {
                    const player2 = playersAtTable[seat2];
                    playerPairs[Math.min(player1, player2)][Math.max(player1, player2)]++;
                }
            }

            // Track 3-player meets
            for (let i = 0; i < 4; i++) {
                for (let j = i + 1; j < 4; j++) {
                    for (let k = j + 1; k < 4; k++) {
                        const trio = [
                            playersAtTable[i],
                            playersAtTable[j],
                            playersAtTable[k]
                        ].sort((a, b) => a - b).join(',');
                        meets3.set(trio, (meets3.get(trio) || 0) + 1);
                    }
                }
            }

            // Track 4-player meets
            const quartet = [...playersAtTable].sort((a, b) => a - b).join(',');
            meets4.set(quartet, (meets4.get(quartet) || 0) + 1);
        }
    }

    // Calculate indirect meetings
    for (let player1 = 1; player1 <= playerCount; player1++) {
        for (let player2 = player1 + 1; player2 <= playerCount; player2++) {
            for (let player3 = 1; player3 <= playerCount; player3++) {
                if (playerPairs[Math.min(player1, player3)][Math.max(player1, player3)] > 0 &&
                    playerPairs[Math.min(player2, player3)][Math.max(player2, player3)] > 0) {
                    indirectMeets[player1][player2]++;
                }
            }
        }
    }

    // Initialize histograms
    const windHist = Array(hanchanCount + 1).fill(0);
    const tableHist = Array(hanchanCount + 1).fill(0);
    const meetHist = Array(hanchanCount + 1).fill(0);
    const indirectMeetHist = Array(playerCount + 1).fill(0);

    // Fill histograms
    for (let player = 1; player <= playerCount; player++) {
        for (let otherPlayer = player + 1; otherPlayer <= playerCount; otherPlayer++) {
            meetHist[playerPairs[player][otherPlayer]]++;
            if (!ignorePlayers.includes(player) && 
                !ignorePlayers.includes(otherPlayer) && 
                !playerPairs[player][otherPlayer]) {
                indirectMeetHist[indirectMeets[player][otherPlayer]]++;
            }
        }
        
        if (!ignorePlayers.includes(player)) {
            for (let wind = 0; wind < 4; wind++) {
                windHist[playerWinds[player][wind]]++;
            }
            for (let table = 0; table < tableCount; table++) {
                tableHist[playerTables[player][table]]++;
            }
        }
    }

    // Count repeats
    const repeat3 = Array.from(meets3.values()).filter(count => count > 1).length;
    const repeat4 = Array.from(meets4.values()).filter(count => count > 1).length;

    // Helper to remove trailing zeros
    const truncateTrailingZeroes = arr => {
        while (arr.length > 0 && arr[arr.length - 1] === 0) {
            arr.pop();
        }
        return arr;
    };

    return {
        meets: truncateTrailingZeroes([...meetHist]),
        indirects: truncateTrailingZeroes([...indirectMeetHist]),
        tables: truncateTrailingZeroes([...tableHist]),
        wind: truncateTrailingZeroes([...windHist]),
        repeat3,
        repeat4
    };
}
