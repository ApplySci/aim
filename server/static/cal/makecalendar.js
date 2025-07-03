// Tournament Calendar System
// Player data from main.csv and team.csv
const TOURNAMENT_DATA = {
    players: [
        // Additional players will be added programmatically
    ],
    teams: [
        // Team data will be added programmatically
    ],
    
    // Create lookup maps for efficient searching
    playersByName: new Map(),
    playersByTable: new Map(), // Map of "round-table" -> [players]
    teamPlayersByName: new Map(), // Map of player name -> team info
    teamPlayersByTable: new Map() // Map of "round-table" -> [team players]
};

// Schedule data extracted from cal.ics
const SCHEDULE_DATA = {
    teamEvent: {
        1: { day: "Wednesday", time: "11:10", date: "2025-07-02" },
        2: { day: "Wednesday", time: "12:50", date: "2025-07-02" },
        3: { day: "Wednesday", time: "15:30", date: "2025-07-02" }
    },
    mainEvent: {
        1: { day: "Thursday", time: "12:50", date: "2025-07-03" },
        2: { day: "Thursday", time: "15:40", date: "2025-07-03" },
        3: { day: "Thursday", time: "17:20", date: "2025-07-03" },
        4: { day: "Thursday", time: "19:00", date: "2025-07-03" },
        5: { day: "Thursday", time: "20:40", date: "2025-07-03" },
        6: { day: "Friday", time: "12:50", date: "2025-07-04" },
        7: { day: "Friday", time: "15:40", date: "2025-07-04" },
        8: { day: "Friday", time: "17:20", date: "2025-07-04" },
        9: { day: "Friday", time: "19:00", date: "2025-07-04" },
        10: { day: "Friday", time: "20:40", date: "2025-07-04" }
    }
};

// Function to get all player data from CSV
function getAllPlayerData() {
    return [
        [1,"Japan","Aki Nikaido",1,1,1,1,1,1,1,1,1,1],
        [2,"Japan","Kenta Kuwada",2,2,2,2,2,2,2,2,2,2],
        [3,"Japan","Kazunori Takizawa",3,3,3,3,3,3,3,3,3,3],
        [4,"Japan","Jun Nishikawa",4,4,4,4,4,4,4,4,4,4],
        [5,"Japan","Rio Tojyo",5,5,5,5,5,5,5,5,5,5],
        [6,"Japan","Yuko Ito",6,6,6,6,6,6,6,6,6,6],
        [7,"Japan","Yu Suzuki",7,7,7,7,7,7,7,7,7,7],
        [8,"Japan","Yukio Oshida",8,8,8,8,8,8,8,8,8,8],
        [9,"Japan","Hidetaka Sakai",9,9,9,9,9,9,9,9,9,9],
        [10,"Japan","Megumu Aikawa",10,10,10,10,10,10,10,10,10,10],
        [11,"Japan","Shota Akutsu",11,11,11,11,11,11,11,11,11,11],
        [12,"Japan","Sho Shiratori",12,12,12,12,12,12,12,12,12,12],
        [13,"Japan","Yoshihiro Matsumoto",13,13,13,13,13,13,13,13,13,13],
        [14,"Japan","Mari Takamiya",14,14,14,14,14,14,14,14,14,14],
        [15,"Japan","Motonari Yoshida",15,15,15,15,15,15,15,15,15,15],
        [16,"Japan","Go Kobayashi",16,16,16,16,16,16,16,16,16,16],
        [17,"Japan","Tomohiro Honda",17,17,17,17,17,17,17,17,17,17],
        [18,"Japan","Saki Kurosawa",18,18,18,18,18,18,18,18,18,18],
        [19,"Japan","Keijun Nara",19,19,19,19,19,19,19,19,19,19],
        [20,"Japan","Satoshi Fujisaki",20,20,20,20,20,20,20,20,20,20],
        [21,"Japan","Hisato Sasaki",21,21,21,21,21,21,21,21,21,21],
        [22,"Japan","Naoya Maeda",22,22,22,22,22,22,22,22,22,22],
        [23,"Japan","Kaori Shimizu",23,23,23,23,23,23,23,23,23,23],
        [24,"Japan","Sayaka Okada",24,24,24,24,24,24,24,24,24,24],
        [25,"Japan","Masaharu Tomotake",25,25,25,25,25,25,25,25,25,25],
        [26,"Japan","Takaya Matsugase",26,26,26,26,26,26,26,26,26,26],
        [27,"Japan","Kazuki Miyazaki",27,27,27,27,27,27,27,27,27,27],
        [28,"Japan","Hiroyuki Ogawa",28,28,28,28,28,28,28,28,28,28],
        [29,"Japan","Takashi Furuhashi",29,29,29,29,29,29,29,29,29,29],
        [30,"Japan","Shunsuke Kikuchi",30,30,30,30,30,30,30,30,30,30],
        [31,"Japan","Tetsuya Tachibana",31,31,31,31,31,31,31,31,31,31],
        [32,"Japan","Asataro Nada",32,32,32,32,32,32,32,32,32,32],
        [33,"Japan","Daisuke Suzuki",33,33,33,33,33,33,33,33,33,33],
        [34,"Japan","Hiro Shibata",34,34,34,34,34,34,34,34,34,34],
        [35,"Japan","Hiroyuki Yamada",35,35,35,35,35,35,35,35,35,35],
        [36,"Japan","Kana Nakada",36,36,36,36,36,36,36,36,36,36],
        [37,"Japan","Kenjiro Fujishima",37,37,37,37,37,37,37,37,37,37],
        [38,"Japan","Naoki Setokuma",38,38,38,38,38,38,38,38,38,38],
        [39,"Japan","Jun Murakami",39,39,39,39,39,39,39,39,39,39],
        [40,"Japan","Hiroshi Daigo",40,40,40,40,40,40,40,40,40,40],
        [41,"Japan","Genta Takeuchi",41,41,41,41,41,41,41,41,41,41],
        [42,"Japan","Seiichi Kondo",42,42,42,42,42,42,42,42,42,42],
        [43,"Japan","Akira Wakutsu",43,43,43,43,43,43,43,43,43,43],
        [44,"Japan","Takaki Asai",44,44,44,44,44,44,44,44,44,44],
        [45,"Japan","Takaharu Oi",45,45,45,45,45,45,45,45,45,45],
        [46,"Japan","Yuumi Uotani",46,46,46,46,46,46,46,46,46,46],
        [47,"Japan","Hiroshi Yamai",47,47,47,47,47,47,47,47,47,47],
        [48,"Japan","Namba Shibukawa",48,48,48,48,48,48,48,48,48,48],
        [49,"Japan","Kenji Katsumata",49,49,49,49,49,49,49,49,49,49],
        [50,"Japan","Makoto Sawazaki",50,50,50,50,50,50,50,50,50,50],
        [51,"Japan","Hiroe Sugawara",51,51,51,51,51,51,51,51,51,51],
        [52,"Japan","Shigekazu Moriyama",52,52,52,52,52,52,52,52,52,52],
        [53,"Japan","Ken Sonoda",53,53,53,53,53,53,53,53,53,53],
        [54,"Japan","Taro Suzuki",54,54,54,54,54,54,54,54,54,54],
        [55,"Japan","Kei Nakabayashi",55,55,55,55,55,55,55,55,55,55],
        [56,"Japan","Kazuma Ishii",56,56,56,56,56,56,56,56,56,56],
        [57,"Japan","Tomohiro Miura",57,57,57,57,57,57,57,57,57,57],
        [58,"Japan","Shingo Hori",58,58,58,58,58,58,58,58,58,58],
        [59,"Japan","Kotaro Uchikawa",59,59,59,59,59,59,59,59,59,59],
        [60,"Japan","Kansuke Sugiura",60,60,60,60,60,60,60,60,60,60],
        [61,"Japan","Masatoshi Sarukawa",61,61,61,61,61,61,61,61,61,61],
        [62,"Japan","Maki Asami",62,62,62,62,62,62,62,62,62,62],
        [63,"Japan","Aiko Hinata",63,63,63,63,63,63,63,63,63,63],
        [64,"Japan","Arisa Date",64,64,64,64,64,64,64,64,64,64],
        [65,"Canada","Michael Hernandez",1,2,3,4,5,6,7,8,9,10],
        [66,"Japan","Takashi Ito",2,3,4,5,6,7,8,9,10,11],
        [67,"Japan","Takuma Jinushi",3,4,5,6,7,8,9,10,11,12],
        [68,"United States","Ray Tan",4,5,6,7,8,9,10,11,12,13],
        [69,"Japan","Maika Tanizaki",5,6,7,8,9,10,11,12,13,14],
        [70,"Canada","Edward Jiayu Zeng",6,7,8,9,10,11,12,13,14,15],
        [71,"Japan","Yurika Aoi",7,8,9,10,11,12,13,14,15,16],
        [72,"United States","Bichen Wang",8,9,10,11,12,13,14,15,16,17],
        [73,"United States","Kinyan Lui",9,10,11,12,13,14,15,16,17,18],
        [74,"Japan","Sakiku Tezuka",10,11,12,13,14,15,16,17,18,19],
        [75,"Japan","Satoshi Akemura",11,12,13,14,15,16,17,18,19,20],
        [76,"Japan","Chifumi Yamawaki",12,13,14,15,16,17,18,19,20,21],
        [77,"Japan","Kyosuke Hyuga",13,14,15,16,17,18,19,20,21,22],
        [78,"Japan","Ｍasaki Iida",14,15,16,17,18,19,20,21,22,23],
        [79,"Japan","Satoru Shibusawa",15,16,17,18,19,20,21,22,23,24],
        [80,"United States","Jing Tu",16,17,18,19,20,21,22,23,24,25],
        [81,"United States","Bob Chow",17,18,19,20,21,22,23,24,25,26],
        [82,"United States","Takahiro Sato",18,19,20,21,22,23,24,25,26,27],
        [83,"United States","Steven Liu",19,20,21,22,23,24,25,26,27,28],
        [84,"United States","Kate Drutskaya",20,21,22,23,24,25,26,27,28,29],
        [85,"United States","Edward Koshimoto",21,22,23,24,25,26,27,28,29,30],
        [86,"United States","Noelle Hui",22,23,24,25,26,27,28,29,30,31],
        [87,"Canada","Grant Mahoney",23,24,25,26,27,28,29,30,31,32],
        [88,"Ireland","Andrew ZP Smith",24,25,26,27,28,29,30,31,32,33],
        [89,"Japan","Kazushi Hayashi",25,26,27,28,29,30,31,32,33,34],
        [90,"Canada","Michael McLeod",26,27,28,29,30,31,32,33,34,35],
        [91,"Japan","Takanori Abe",27,28,29,30,31,32,33,34,35,36],
        [92,"Japan","Shigefumi Tanii",28,29,30,31,32,33,34,35,36,37],
        [93,"Japan","Masao Kuroki",29,30,31,32,33,34,35,36,37,38],
        [94,"Japan","Risako Kaji",30,31,32,33,34,35,36,37,38,39],
        [95,"Japan","Kazuharu Hachiya",31,32,33,34,35,36,37,38,39,40],
        [96,"Japan","Kozue Miyauchi",32,33,34,35,36,37,38,39,40,41],
        [97,"Hungary","Tamás Erdős",33,34,35,36,37,38,39,40,41,42],
        [98,"Japan","Noriyuki Nakajima",34,35,36,37,38,39,40,41,42,43],
        [99,"Japan","Toshiyuki Tomozoe",35,36,37,38,39,40,41,42,43,44],
        [100,"United States","Dustin Fries",36,37,38,39,40,41,42,43,44,45],
        [101,"United States","Dennis Sharkey",37,38,39,40,41,42,43,44,45,46],
        [102,"United States","Hiroshi Yoshida",38,39,40,41,42,43,44,45,46,47],
        [103,"Canada","Carl Brunelle",39,40,41,42,43,44,45,46,47,48],
        [104,"Japan","Kana Nakata",40,41,42,43,44,45,46,47,48,49],
        [105,"United States","Dani Moreno",41,42,43,44,45,46,47,48,49,50],
        [106,"Japan","Kei Takahashi",42,43,44,45,46,47,48,49,50,51],
        [107,"Japan","Masaki Ito",43,44,45,46,47,48,49,50,51,52],
        [108,"Japan","Yuichi Fukushima",44,45,46,47,48,49,50,51,52,53],
        [109,"United States","Brian Wen",45,46,47,48,49,50,51,52,53,54],
        [110,"United States","Josh Havens",46,47,48,49,50,51,52,53,54,55],
        [111,"Japan","Yoshikazu Shibata",47,48,49,50,51,52,53,54,55,56],
        [112,"Japan","Eigo Watanabe",48,49,50,51,52,53,54,55,56,57],
        [113,"United States","Nathanael Kozinski",49,50,51,52,53,54,55,56,57,58],
        [114,"Japan","Tetsuya Fujimoto",50,51,52,53,54,55,56,57,58,59],
        [115,"Japan","Tomohiko Nishida",51,52,53,54,55,56,57,58,59,60],
        [116,"Japan","Hiroaki Tamotsu",52,53,54,55,56,57,58,59,60,61],
        [117,"Japan","Takeshi Ohtani",53,54,55,56,57,58,59,60,61,62],
        [118,"Japan","Yukiko Izumi",54,55,56,57,58,59,60,61,62,63],
        [119,"United States","Yishen Wu",55,56,57,58,59,60,61,62,63,64],
        [120,"Japan","Yoichiro Koide",56,57,58,59,60,61,62,63,64,1],
        [121,"Japan","Tomonori Koshino",57,58,59,60,61,62,63,64,1,2],
        [122,"United States","Cristi Magracia",58,59,60,61,62,63,64,1,2,3],
        [123,"Japan","Kyosuke Kawai",59,60,61,62,63,64,1,2,3,4],
        [124,"Japan","Eiji Kanasugi",60,61,62,63,64,1,2,3,4,5],
        [125,"Japan","Sho Nakagawa",61,62,63,64,1,2,3,4,5,6],
        [126,"United States","Stanley Deng",62,63,64,1,2,3,4,5,6,7],
        [127,"Japan","Ryo Yamamoto",63,64,1,2,3,4,5,6,7,8],
        [128,"Japan","Noriyuki Kiriyama",64,1,2,3,4,5,6,7,8,9],
        [129,"Australia","Charles Phan",1,3,5,7,9,11,13,15,17,19],
        [130,"South Korea","Yonga Kim",2,4,6,8,10,12,14,16,18,20],
        [131,"Chinese Taipei","Pei-jyun Shih",3,5,7,9,11,13,15,17,19,21],
        [132,"Singapore","Ang Zhen Yao",4,6,8,10,12,14,16,18,20,22],
        [133,"Independent","Andrei Klimov",5,7,9,11,13,15,17,19,21,23],
        [134,"South Korea","Hyojeong Shim",6,8,10,12,14,16,18,20,22,24],
        [135,"South Korea","Junseok Yoon",7,9,11,13,15,17,19,21,23,25],
        [136,"Singapore","Timothy Ling",8,10,12,14,16,18,20,22,24,26],
        [137,"Australia","Aaron Chee",9,11,13,15,17,19,21,23,25,27],
        [138,"Hong Kong","Kazusa Cheung",10,12,14,16,18,20,22,24,26,28],
        [139,"Indonesia","Dicky Suharli",11,13,15,17,19,21,23,25,27,29],
        [140,"Indonesia","David Danihardja",12,14,16,18,20,22,24,26,28,30],
        [141,"Vietnam","Phan Nguyen Hung Cuong",13,15,17,19,21,23,25,27,29,31],
        [142,"China","XuLiang Qian",14,16,18,20,22,24,26,28,30,32],
        [143,"Slovakia","Michal Marko",15,17,19,21,23,25,27,29,31,33],
        [144,"Chinese Taipei","Yu Ting Cheng",16,18,20,22,24,26,28,30,32,34],
        [145,"South Korea","Jin soo Kim",17,19,21,23,25,27,29,31,33,35],
        [146,"Independent","Vladislav Pliasunov",18,20,22,24,26,28,30,32,34,36],
        [147,"Singapore","Destin Ngeow",19,21,23,25,27,29,31,33,35,37],
        [148,"Brazil","Murilo Bordignon",20,22,24,26,28,30,32,34,36,38],
        [149,"China","Jinrui Zhu",21,23,25,27,29,31,33,35,37,39],
        [150,"Argentina","Patricio Bruni",22,24,26,28,30,32,34,36,38,40],
        [151,"Uruguay","Luca Ferrari",23,25,27,29,31,33,35,37,39,41],
        [152,"Uruguay","Abril Rodino",24,26,28,30,32,34,36,38,40,42],
        [153,"South Korea","James Yu",25,27,29,31,33,35,37,39,41,43],
        [154,"Brazil","Sabrina Simao",26,28,30,32,34,36,38,40,42,44],
        [155,"Independent","Kirill Khromov",27,29,31,33,35,37,39,41,43,45],
        [156,"Hong Kong","Bary Liu",28,30,32,34,36,38,40,42,44,46],
        [157,"Australia","Richard Kiing",29,31,33,35,37,39,41,43,45,47],
        [158,"Hong Kong","Russell Chan",30,32,34,36,38,40,42,44,46,48],
        [159,"Brazil","Akira Kobayashi",31,33,35,37,39,41,43,45,47,49],
        [160,"Slovenia","Jernej Pangerc",32,34,36,38,40,42,44,46,48,50],
        [161,"Chile","César Roudergue Fuentes",33,35,37,39,41,43,45,47,49,51],
        [162,"Chinese Taipei","Che-an Shih \"Zyn\"",34,36,38,40,42,44,46,48,50,52],
        [163,"Brazil","Amauri Murai",35,37,39,41,43,45,47,49,51,53],
        [164,"South Korea","Junhyung Kwon",36,38,40,42,44,46,48,50,52,54],
        [165,"Chinese Taipei","Fang-Liang Liu",37,39,41,43,45,47,49,51,53,55],
        [166,"Australia","Arthur Chen",38,40,42,44,46,48,50,52,54,56],
        [167,"China","Wenlong Li",39,41,43,45,47,49,51,53,55,57],
        [168,"Hong Kong","Lucas Ho",40,42,44,46,48,50,52,54,56,58],
        [169,"Hong Kong","Stephen Cheung",41,43,45,47,49,51,53,55,57,59],
        [170,"Czech","Martin Rydland",42,44,46,48,50,52,54,56,58,60],
        [171,"Chile","Sebastián Paredes",43,45,47,49,51,53,55,57,59,61],
        [172,"Hong Kong","Stephen Leung",44,46,48,50,52,54,56,58,60,62],
        [173,"Vietnam","Thanh Hai Hoang",45,47,49,51,53,55,57,59,61,63],
        [174,"Brazil","Lucas Secomandi",46,48,50,52,54,56,58,60,62,64],
        [175,"Australia","Trevor Yau",47,49,51,53,55,57,59,61,63,1],
        [176,"China","Haoran Xia",48,50,52,54,56,58,60,62,64,2],
        [177,"Independent","Aleksey Leontyev",49,51,53,55,57,59,61,63,1,3],
        [178,"Chile","Cristian Abarza",50,52,54,56,58,60,62,64,2,4],
        [179,"Argentina","Nicolas Ishihara",51,53,55,57,59,61,63,1,3,5],
        [180,"China","TONG TONG",52,54,56,58,60,62,64,2,4,6],
        [181,"Independent","Natalya Maximova",53,55,57,59,61,63,1,3,5,7],
        [182,"China","ZhenWei Lin",54,56,58,60,62,64,2,4,6,8],
        [183,"China","Teng Xu",55,57,59,61,63,1,3,5,7,9],
        [184,"South Korea","Lim Heonwoo",56,58,60,62,64,2,4,6,8,10],
        [185,"Singapore","Yang Yee",57,59,61,63,1,3,5,7,9,11],
        [186,"Independent","Vladimir Nadanyan",58,60,62,64,2,4,6,8,10,12],
        [187,"South Korea","CS Kim",59,61,63,1,3,5,7,9,11,13],
        [188,"Argentina","Facundo Zorrilla",60,62,64,2,4,6,8,10,12,14],
        [189,"China","Yunfei Gao",61,63,1,3,5,7,9,11,13,15],
        [190,"Independent","Raziya Bizhanova",62,64,2,4,6,8,10,12,14,16],
        [191,"Chinese Taipei","Po-Ping Chang",63,1,3,5,7,9,11,13,15,17],
        [192,"China","Haomin Gao",64,2,4,6,8,10,12,14,16,18],
        [193,"Austria","Lena Weinguny",1,4,7,10,13,16,19,22,25,28],
        [194,"Belgium","Arnaud Renard",2,5,8,11,14,17,20,23,26,29],
        [195,"Belgium","Haddou Keil",3,6,9,12,15,18,21,24,27,30],
        [196,"Ukraine","Anna Zubenko",4,7,10,13,16,19,22,25,28,31],
        [197,"Germany","Theresa Goeser",5,8,11,14,17,20,23,26,29,32],
        [198,"Denmark","Eskild Middelboe",6,9,12,15,18,21,24,27,30,33],
        [199,"Spain","Linxuan He",7,10,13,16,19,22,25,28,31,34],
        [200,"Austria","Alexander Doppelhofer",8,11,14,17,20,23,26,29,32,35],
        [201,"France","Cecile Blanc",9,12,15,18,21,24,27,30,33,36],
        [202,"Ukraine","Vitalii Balaniuk",10,13,16,19,22,25,28,31,34,37],
        [203,"Poland","Mateusz Wozniak",11,14,17,20,23,26,29,32,35,38],
        [204,"Netherlands","Kan Chen",12,15,18,21,24,27,30,33,36,39],
        [205,"Switzerland","Thibaut Arnold",13,16,19,22,25,28,31,34,37,40],
        [206,"Germany","Manuel Kameda-Schlich",14,17,20,23,26,29,32,35,38,41],
        [207,"Finland","Henri Makela",15,18,21,24,27,30,33,36,39,42],
        [208,"France","Sylvain Malbec",16,19,22,25,28,31,34,37,40,43],
        [209,"Sweden","Christos Charalampous",17,20,23,26,29,32,35,38,41,44],
        [210,"France","Steven Hue",18,21,24,27,30,33,36,39,42,45],
        [211,"Switzerland","Kohei Miyake",19,22,25,28,31,34,37,40,43,46],
        [212,"United Kingdom","Christopher Endicott",20,23,26,29,32,35,38,41,44,47],
        [213,"Sweden","Xiaochen Zhu",21,24,27,30,33,36,39,42,45,48],
        [214,"Finland","Joel Siirto",22,25,28,31,34,37,40,43,46,49],
        [215,"Austria","Lukas Gerhold",23,26,29,32,35,38,41,44,47,50],
        [216,"Poland","Artur Libich",24,27,30,33,36,39,42,45,48,51],
        [217,"Belgium","Linh Van Leuven",25,28,31,34,37,40,43,46,49,52],
        [218,"Norway","Jo Frostad",26,29,32,35,38,41,44,47,50,53],
        [219,"France","Alex Leung",27,30,33,36,39,42,45,48,51,54],
        [220,"Portugal","Sérgio Matos Lima",28,31,34,37,40,43,46,49,52,55],
        [221,"Finland","Klaudia Lensu",29,32,35,38,41,44,47,50,53,56],
        [222,"United Kingdom","John Duckworth",30,33,36,39,42,45,48,51,54,57],
        [223,"Germany","Junyu Wang",31,34,37,40,43,46,49,52,55,58],
        [224,"United Kingdom","Tom Pearson",32,35,38,41,44,47,50,53,56,59],
        [225,"Poland","Dominik Jarno",33,36,39,42,45,48,51,54,57,60],
        [226,"Finland","Jouni Lehtinen",34,37,40,43,46,49,52,55,58,61],
        [227,"Netherlands","Junjie You",35,38,41,44,47,50,53,56,59,62],
        [228,"Spain","Yeyin Lu",36,39,42,45,48,51,54,57,60,63],
        [229,"Netherlands","Ruud Cremers",37,40,43,46,49,52,55,58,61,64],
        [230,"Finland","Mikko Aarnos",38,41,44,47,50,53,56,59,62,1],
        [231,"Portugal","Rodrigo Lopes",39,42,45,48,51,54,57,60,63,2],
        [232,"France","Manuel Tertre",40,43,46,49,52,55,58,61,64,3],
        [233,"Ukraine","Sveta Yaremenko",41,44,47,50,53,56,59,62,1,4],
        [234,"United Kingdom","Martin Lester",42,45,48,51,54,57,60,63,2,5],
        [235,"Romania","Rene Khezam",43,46,49,52,55,58,61,64,3,6],
        [236,"Germany","Kenneth Chan",44,47,50,53,56,59,62,1,4,7],
        [237,"France","Valentin Courtois",45,48,51,54,57,60,63,2,5,8],
        [238,"Romania","Michael van der Sluijs",46,49,52,55,58,61,64,3,6,9],
        [239,"Poland","Michal Waliszewski",47,50,53,56,59,62,1,4,7,10],
        [240,"Poland","Łukasz Grzybowski",48,51,54,57,60,63,2,5,8,11],
        [241,"France","Joe-Calberson Huynh",49,52,55,58,61,64,3,6,9,12],
        [242,"France","Jeremie Pierard de Maujouy",50,53,56,59,62,1,4,7,10,13],
        [243,"Ukraine","Kateryna Kondratenko",51,54,57,60,63,2,5,8,11,14],
        [244,"Belgium","Henri Devillez",52,55,58,61,64,3,6,9,12,15],
        [245,"Italy","Marco Montebelli",53,56,59,62,1,4,7,10,13,16],
        [246,"Ukraine","Maksym Ivanov",54,57,60,63,2,5,8,11,14,17],
        [247,"United States","Edwin Dizon",55,58,61,64,3,6,9,12,15,18],
        [248,"Denmark","Jesper Nøhr",56,59,62,1,4,7,10,13,16,19],
        [249,"Denmark","Bao Zheng Liu",57,60,63,2,5,8,11,14,17,20],
        [250,"Sweden","Fang He",58,61,64,3,6,9,12,15,18,21],
        [251,"Poland","Ula Szudlich",59,62,1,4,7,10,13,16,19,22],
        [252,"Austria","Anton Lu",60,63,2,5,8,11,14,17,20,23],
        [253,"United Kingdom","Gemma Sakamoto",61,64,3,6,9,12,15,18,21,24],
        [254,"Netherlands","Timo Heemstra",62,1,4,7,10,13,16,19,22,25],
        [255,"Italy","Loris Langeri",63,2,5,8,11,14,17,20,23,26],
        [256,"Poland","Olga Igarashi",64,3,6,9,12,15,18,21,24,27]
    ];
}

// Function to get all team data from team.csv
function getAllTeamData() {
    return [
        [1,"Argentina/Uruguay",150,"Argentina","Patricio Bruni",36,27,28],
        [1,"Argentina/Uruguay",152,"Uruguay","Abril Rodino",29,40,42],
        [1,"Argentina/Uruguay",179,"Argentina","Nicolas Ishihara",6,18,23],
        [1,"Argentina/Uruguay",188,"Argentina","Facundo Zorrilla",30,29,15],
        [2,"Australia",129,"Australia","Charles Phan",43,"",2],
        [2,"Australia",137,"Australia","Aaron Chee","",15,27],
        [2,"Australia",157,"Australia","Richard Kiing",3,23,5],
        [2,"Australia",166,"Australia","Arthur Chen",42,44,""],
        [2,"Australia",175,"Australia","Trevor Yau",44,40,7],
        [3,"Austria",193,"Austria","Lena Weinguny",40,3,11],
        [3,"Austria",200,"Austria","Alexander Doppelhofer",44,2,26],
        [3,"Austria",215,"Austria","Lukas Gerhold",37,38,24],
        [3,"Austria",252,"Austria","Anton Lu",39,11,41],
        [4,"Belgium",194,"Belgium","Arnaud Renard",22,9,36],
        [4,"Belgium",195,"Belgium","Haddou Keil",14,22,37],
        [4,"Belgium",217,"Belgium","Linh Van Leuven",21,31,3],
        [4,"Belgium",244,"Belgium","Henri Devillez",18,34,13],
        [5,"Brazil",148,"Brazil","Murilo Bordignon",9,35,4],
        [5,"Brazil",159,"Brazil","Akira Kobayashi",32,32,9],
        [5,"Brazil",163,"Brazil","Amauri Murai",3,44,10],
        [5,"Brazil",174,"Brazil","Lucas Secomandi",10,1,26],
        [6,"Canada",65,"Canada","Michael Hernandez",7,40,36],
        [6,"Canada",70,"Canada","Edward Jiayu Zeng",29,43,17],
        [6,"Canada",87,"Canada","Grant Mahoney","",7,4],
        [6,"Canada",90,"Canada","Michael McLeod",16,"",39],
        [6,"Canada",103,"Canada","Carl Brunelle",10,31,""],
        [7,"Chile/Uruguay",151,"Uruguay","Luca Ferrari",1,25,20],
        [7,"Chile/Uruguay",161,"Chile","César Roudergue Fuentes",28,13,1],
        [7,"Chile/Uruguay",171,"Chile","Sebastián Paredes",20,2,43],
        [7,"Chile/Uruguay",178,"Chile","Cristian Abarza",45,42,39],
        [8,"China A",142,"China","XuLiang Qian",11,38,30],
        [8,"China A",167,"China","Wenlong Li",32,41,3],
        [8,"China A",183,"China","Teng Xu",42,19,15],
        [8,"China A",189,"China","Yunfei Gao",12,26,19],
        [9,"China B",149,"China","Jinrui Zhu",14,27,12],
        [9,"China B",176,"China","Haoran Xia",1,45,20],
        [9,"China B",182,"China","ZhenWei Lin",10,25,45],
        [9,"China B",192,"China","Haomin Gao",8,42,34],
        [10,"Chinese Taipei",131,"Chinese Taipei","Pei-jyun Shih",17,"",22],
        [10,"Chinese Taipei",144,"Chinese Taipei","Yu Ting Cheng",8,14,27],
        [10,"Chinese Taipei",162,"Chinese Taipei","Che-an Shih \"Zyn\"",41,36,20],
        [10,"Chinese Taipei",165,"Chinese Taipei","Fang-Liang Liu","",6,5],
        [10,"Chinese Taipei",191,"Chinese Taipei","Po-Ping Chang",13,8,""],
        [11,"Denmark/Ireland",88,"Ireland","Andrew ZP Smith",35,20,7],
        [11,"Denmark/Ireland",198,"Denmark","Eskild Middelboe",19,21,27],
        [11,"Denmark/Ireland",248,"Denmark","Jesper Nøhr",1,1,38],
        [11,"Denmark/Ireland",249,"Denmark","Bao Zheng Liu",5,12,2],
        [12,"Finland",207,"Finland","Henri Makela",36,17,38],
        [12,"Finland",214,"Finland","Joel Siirto",7,"",6],
        [12,"Finland",221,"Finland","Klaudia Lensu",3,9,""],
        [12,"Finland",226,"Finland","Jouni Lehtinen","",21,29],
        [12,"Finland",230,"Finland","Mikko Aarnos",27,19,8],
        [13,"France A",208,"France","Sylvain Malbec",9,8,33],
        [13,"France A",210,"France","Steven Hue",5,5,44],
        [13,"France A",232,"France","Manuel Tertre",35,15,25],
        [13,"France A",242,"France","Jeremie Pierard de Maujouy",2,10,9],
        [14,"France B",201,"France","Cecile Blanc",11,18,23],
        [14,"France B",219,"France","Alex Leung",32,32,31],
        [14,"France B",237,"France","Valentin Courtois",31,30,35],
        [14,"France B",241,"France","Joe-Calberson Huynh",16,11,7],
        [15,"Germany",197,"Germany","Theresa Goeser",28,30,37],
        [15,"Germany",206,"Germany","Manuel Kameda-Schlich",26,17,28],
        [15,"Germany",223,"Germany","Junyu Wang",2,7,13],
        [15,"Germany",236,"Germany","Kenneth Chan",40,33,42],
        [16,"Hong Kong",138,"Hong Kong","Kazusa Cheung",22,4,32],
        [16,"Hong Kong",156,"Hong Kong","Bary Liu",33,6,""],
        [16,"Hong Kong",168,"Hong Kong","Lucas Ho",18,41,12],
        [16,"Hong Kong",169,"Hong Kong","Stephen Cheung",27,44,22],
        [16,"Hong Kong",172,"Hong Kong","Stephen Leung","","",40],
        [17,"Independent A",146,"Independent","Vladislav Pliasunov",12,10,33],
        [17,"Independent A",155,"Independent","Kirill Khromov",34,28,""],
        [17,"Independent A",177,"Independent","Aleksey Leontyev",41,"",13],
        [17,"Independent A",181,"Independent","Natalya Maximova",35,8,16],
        [17,"Independent A",186,"Independent","Vladimir Nadanyan","",20,35],
        [18,"Independent B",133,"Independent","Andrei Klimov",4,42,42],
        [18,"Independent B",158,"Hong Kong","Russell Chan",15,29,29],
        [18,"Independent B",190,"Independent","Raziya Bizhanova",44,19,15],
        [18,"Independent B",301,"United States","Allon Scheyer",2,26,28],
        [19,"Indonesia/Vietnam",139,"Indonesia","Dicky Suharli",15,5,4],
        [19,"Indonesia/Vietnam",140,"Indonesia","David Danihardja",4,16,37],
        [19,"Indonesia/Vietnam",141,"Vietnam","Phan Nguyen Hung Cuong",23,30,36],
        [19,"Indonesia/Vietnam",173,"Vietnam","Thanh Hai Hoang",13,4,19],
        [20,"Italy/Switzerland",205,"Switzerland","Thibaut Arnold",9,15,18],
        [20,"Italy/Switzerland",211,"Switzerland","Kohei Miyake",28,37,12],
        [20,"Italy/Switzerland",245,"Italy","Marco Montebelli",25,33,40],
        [20,"Italy/Switzerland",255,"Italy","Loris Langeri",38,38,16],
        [21,"Japan Full National Team A",41,"Japan","Genta Takeuchi",4,35,7],
        [21,"Japan Full National Team A",45,"Japan","Takaharu Oi",34,11,27],
        [21,"Japan Full National Team A",54,"Japan","Taro Suzuki",19,1,33],
        [21,"Japan Full National Team A",64,"Japan","Arisa Date",31,6,40],
        [22,"Japan Full National Team B",17,"Japan","Tomohiro Honda",23,30,22],
        [22,"Japan Full National Team B",21,"Japan","Hisato Sasaki",40,42,35],
        [22,"Japan Full National Team B",55,"Japan","Kei Nakabayashi",27,15,14],
        [22,"Japan Full National Team B",303,"Japan","Akina Mizuhara",43,7,5],
        [23,"Japan Full National Team C",10,"Japan","Megumu Aikawa",16,3,20],
        [23,"Japan Full National Team C",40,"Japan","Hiroshi Daigo",33,24,21],
        [23,"Japan Full National Team C",49,"Japan","Kenji Katsumata",8,20,8],
        [23,"Japan Full National Team C",53,"Japan","Ken Sonoda",11,13,9],
        [24,"Japan Full National Team D",7,"Japan","Yu Suzuki",3,29,11],
        [24,"Japan Full National Team D",12,"Japan","Sho Shiratori",24,28,6],
        [24,"Japan Full National Team D",46,"Japan","Yuumi Uotani",12,37,1],
        [24,"Japan Full National Team D",58,"Japan","Shingo Hori",1,41,28],
        [25,"Japan Women's National Team",1,"Japan","Aki Nikaido",44,33,42],
        [25,"Japan Women's National Team",18,"Japan","Saki Kurosawa",30,36,43],
        [25,"Japan Women's National Team",62,"Japan","Maki Asami",41,21,31],
        [25,"Japan Women's National Team",63,"Japan","Aiko Hinata",15,16,37],
        [26,"Japan Over-60 National Team",50,"Japan","Makoto Sawazaki",6,23,""],
        [26,"Japan Over-60 National Team",52,"Japan","Shigekazu Moriyama",2,"",10],
        [26,"Japan Over-60 National Team",304,"Japan","Kiyoshi Niitsu",22,39,26],
        [26,"Japan Over-60 National Team",305,"Japan","Seiichi Kondo",25,17,13],
        [26,"Japan Over-60 National Team",306,"Japan","Asataro Nada","",26,30],
        [27,"Japan Under-29 National Team",2,"Japan","Kenta Kuwada",26,31,2],
        [27,"Japan Under-29 National Team",11,"Japan","Shota Akutsu",7,40,18],
        [27,"Japan Under-29 National Team",307,"Japan","Riki Aruga",45,5,36],
        [27,"Japan Under-29 National Team",308,"Japan","Yuri Asahina",28,22,44],
        [28,"Japan Mixed Pro Team",8,"Japan","Yukio Oshida",21,32,""],
        [28,"Japan Mixed Pro Team",38,"Japan","Naoki Setokuma","",9,19],
        [28,"Japan Mixed Pro Team",56,"Japan","Kazuma Ishii",36,4,45],
        [28,"Japan Mixed Pro Team",309,"Japan","Geki Shimoishi",39,43,38],
        [28,"Japan Mixed Pro Team",310,"Japan","Takashi Kohno",14,"",41],
        [29,"Netherlands",204,"Netherlands","Kan Chen",38,14,34],
        [29,"Netherlands",227,"Netherlands","Junjie You",45,4,8],
        [29,"Netherlands",229,"Netherlands","Ruud Cremers",5,17,21],
        [29,"Netherlands",254,"Netherlands","Chun Man",23,34,14],
        [30,"Poland A",203,"Poland","Mateusz Wozniak",23,13,32],
        [30,"Poland A",216,"Poland","Artur Libich",19,12,16],
        [30,"Poland A",225,"Poland","Dominik Jarno",10,9,45],
        [30,"Poland A",239,"Poland","Michal Waliszewski",31,18,23],
        [31,"Poland B",240,"Poland","Łukasz Grzybowski",6,23,14],
        [31,"Poland B",251,"Poland","Ula Szudlich",18,39,10],
        [31,"Poland B",256,"Poland","Olga Igarashi",42,24,29],
        [31,"Poland B",302,"Independent","Itaru Soga",26,10,30],
        [32,"Portugal/Spain",199,"Spain","Linxuan He",24,29,19],
        [32,"Portugal/Spain",220,"Portugal","Sérgio Matos Lima",42,23,21],
        [32,"Portugal/Spain",228,"Spain","Yeyin Lu",5,22,5],
        [32,"Portugal/Spain",231,"Portugal","Rodrigo Lopes",20,7,16],
        [33,"Romania/Hungary/Norway",97,"Hungary","Tamás Erdős",12,43,6],
        [33,"Romania/Hungary/Norway",218,"Norway","Jo Frostad",20,16,30],
        [33,"Romania/Hungary/Norway",235,"Romania","Rene Khezam",37,44,8],
        [33,"Romania/Hungary/Norway",238,"Romania","Michael van der Sluijs",33,31,12],
        [34,"Singapore",132,"Singapore","Ang Zhen Yao",14,34,22],
        [34,"Singapore",136,"Singapore","Timothy Ling",21,8,2],
        [34,"Singapore",147,"Singapore","Destin Ngeow",43,45,3],
        [34,"Singapore",185,"Singapore","Yang Yee",18,35,44],
        [35,"Slovenia/Czech/Slovakia",143,"Slovakia","Michal Marko",38,6,25],
        [35,"Slovenia/Czech/Slovakia",160,"Slovenia","Jernej Pangerc",13,22,29],
        [35,"Slovenia/Czech/Slovakia",170,"Czech","Martin Rydland",11,1,1],
        [35,"Slovenia/Czech/Slovakia",247,"United States","Edwin Dizon",33,45,43],
        [36,"South Korea A",130,"South Korea","Yonga Kim",41,11,43],
        [36,"South Korea A",145,"South Korea","Jin soo Kim",34,33,24],
        [36,"South Korea A",164,"South Korea","Junhyung Kwon",39,10,39],
        [36,"South Korea A",184,"South Korea","Lim Heonwoo",16,2,17],
        [37,"South Korea B",134,"South Korea","Hyojeong Shim",26,28,41],
        [37,"South Korea B",135,"South Korea","Junseok Yoon",30,26,26],
        [37,"South Korea B",153,"South Korea","James Yu",6,37,32],
        [37,"South Korea B",187,"South Korea","CS Kim",24,27,44],
        [38,"Sweden",196,"Ukraine","Anna Zubenko",17,21,31],
        [38,"Sweden",209,"Sweden","Christos Charalampous",37,34,11],
        [38,"Sweden",213,"Sweden","Xiaochen Zhu",38,12,35],
        [38,"Sweden",250,"Sweden","Fang He",25,36,17],
        [39,"Ukraine",202,"Ukraine","Vitalii Balaniuk",43,25,18],
        [39,"Ukraine",233,"Ukraine","Sveta Yaremenko",27,24,25],
        [39,"Ukraine",243,"Ukraine","Kateryna Kondratenko",7,12,24],
        [39,"Ukraine",246,"Ukraine","Maksym Ivanov",22,36,14],
        [40,"United Kingdom",212,"United Kingdom","Christopher Endicott",20,3,32],
        [40,"United Kingdom",222,"United Kingdom","John Duckworth",36,39,24],
        [40,"United Kingdom",224,"United Kingdom","Tom Pearson",29,19,39],
        [40,"United Kingdom",234,"United Kingdom","Martin Lester",17,14,34],
        [41,"United States A",84,"United States","Kate Drutskaya",35,27,40],
        [41,"United States A",86,"United States","Noelle Hui",25,43,1],
        [41,"United States A",100,"United States","Dustin Fries",37,28,25],
        [41,"United States A",110,"United States","Josh Havens",21,45,33],
        [42,"United States B",72,"United States","Bichen Wang",24,39,9],
        [42,"United States B",80,"United States","Jing Tu",32,5,17],
        [42,"United States B",85,"United States","Edward Koshimoto",15,18,21],
        [42,"United States B",126,"United States","Stanley Deng",4,38,45],
        [43,"United States C",81,"United States","Bob Chow",34,16,41],
        [43,"United States C",102,"United States","Hiroshi Yoshida",17,25,38],
        [43,"United States C",119,"United States","Yishen Wu",45,35,18],
        [43,"United States C",122,"United States","Cristi Magracia",31,3,4],
        [44,"United States D",68,"United States","Ray Tan",30,20,15],
        [44,"United States D",82,"United States","Takahiro Sato",9,24,6],
        [44,"United States D",83,"United States","Steven Liu",8,37,31],
        [44,"United States D",113,"United States","Nathanael Kozinski",40,14,23],
        [45,"United States E",73,"United States","Kinyan Lui",39,32,3],
        [45,"United States E",101,"United States","Dennis Sharkey",29,2,34],
        [45,"United States E",105,"United States","Dani Moreno",13,13,11],
        [45,"United States E",109,"United States","Brian Wen",19,41,10]
    ];
}

// Function to add all player data from CSV
function initializeTournamentData() {
    const csvData = getAllPlayerData();
    const teamData = getAllTeamData();
    
    // Clear existing data
    TOURNAMENT_DATA.players = [];
    TOURNAMENT_DATA.teams = [];
    TOURNAMENT_DATA.playersByName.clear();
    TOURNAMENT_DATA.playersByTable.clear();
    TOURNAMENT_DATA.teamPlayersByName.clear();
    TOURNAMENT_DATA.teamPlayersByTable.clear();
    
    // Process each main event player
    csvData.forEach(row => {
        const player = {
            id: row[0],
            country: row[1],
            name: row[2],
            tables: row.slice(3, 13) // columns 3-12 are the 10 rounds
        };
        
        TOURNAMENT_DATA.players.push(player);
        TOURNAMENT_DATA.playersByName.set(player.name, player);
        
        // Build table lookup map for main event
        for (let round = 0; round < 10; round++) {
            const tableKey = `${round + 1}-${player.tables[round]}`;
            if (!TOURNAMENT_DATA.playersByTable.has(tableKey)) {
                TOURNAMENT_DATA.playersByTable.set(tableKey, []);
            }
            TOURNAMENT_DATA.playersByTable.get(tableKey).push(player);
        }
    });
    
    // Process each team event player
    teamData.forEach(row => {
        const teamPlayer = {
            teamNo: row[0],
            teamName: row[1],
            playerId: row[2],
            country: row[3],
            name: row[4],
            tables: [row[5], row[6], row[7]] // 3 rounds for team event
        };
        
        TOURNAMENT_DATA.teams.push(teamPlayer);
        TOURNAMENT_DATA.teamPlayersByName.set(teamPlayer.name, teamPlayer);
        
        // Build table lookup map for team event
        for (let round = 0; round < 3; round++) {
            const tableNumber = teamPlayer.tables[round];
            if (tableNumber !== "" && tableNumber !== null && tableNumber !== undefined) {
                const tableKey = `${round + 1}-${tableNumber}`;
                if (!TOURNAMENT_DATA.teamPlayersByTable.has(tableKey)) {
                    TOURNAMENT_DATA.teamPlayersByTable.set(tableKey, []);
                }
                TOURNAMENT_DATA.teamPlayersByTable.get(tableKey).push(teamPlayer);
            }
        }
    });
}

// Function to get table partners for a specific player and round
function getTablePartners(playerName, round) {
    const player = TOURNAMENT_DATA.playersByName.get(playerName);
    if (!player) return null;
    
    const tableNumber = player.tables[round - 1];
    const tableKey = `${round}-${tableNumber}`;
    const tablemates = TOURNAMENT_DATA.playersByTable.get(tableKey) || [];
    
    return {
        round: round,
        table: tableNumber,
        player: player,
        tablemates: tablemates.filter(p => p.id !== player.id)
    };
}

// Function to get all rounds for a player
function getPlayerSchedule(playerName) {
    const schedule = [];
    for (let round = 1; round <= 10; round++) {
        const roundInfo = getTablePartners(playerName, round);
        if (roundInfo) {
            schedule.push(roundInfo);
        }
    }
    return schedule;
}

// Function to get table partners for team event
function getTeamTablePartners(playerName, round) {
    const teamPlayer = TOURNAMENT_DATA.teamPlayersByName.get(playerName);
    if (!teamPlayer) return null;
    
    const tableNumber = teamPlayer.tables[round - 1];
    if (!tableNumber || tableNumber === "" || tableNumber === null || tableNumber === undefined) {
        return null; // Player doesn't play this round
    }
    
    const tableKey = `${round}-${tableNumber}`;
    const tablemates = TOURNAMENT_DATA.teamPlayersByTable.get(tableKey) || [];
    
    return {
        round: round,
        table: tableNumber,
        teamPlayer: teamPlayer,
        tablemates: tablemates.filter(p => p.playerId !== teamPlayer.playerId)
    };
}

// Function to get team schedule for a player
function getTeamPlayerSchedule(playerName) {
    const schedule = [];
    for (let round = 1; round <= 3; round++) {
        const roundInfo = getTeamTablePartners(playerName, round);
        if (roundInfo) {
            schedule.push(roundInfo);
        }
    }
    return schedule;
}

// Function to get all player names for typeahead
function getAllPlayerNames() {
    return TOURNAMENT_DATA.players.map(p => p.name).sort();
}

// UI Variables and Functions
let allPlayerNames = [];

// Function to get URL parameters
function getUrlParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

// Function to find player name by ID
function getPlayerNameById(playerId) {
    const player = TOURNAMENT_DATA.players.find(p => p.id == playerId);
    return player ? player.name : null;
}

function setupTypeahead() {
    const searchInput = document.getElementById('playerSearch');
    const suggestionsDiv = document.getElementById('suggestions');
    
    // Load all player names
    allPlayerNames = getAllPlayerNames();
    
    searchInput.addEventListener('input', function() {
        const query = this.value.toLowerCase().trim();
        
        if (query.length < 2) {
            suggestionsDiv.style.display = 'none';
            return;
        }
        
        // Filter players
        const matches = allPlayerNames.filter(name => 
            name.toLowerCase().includes(query)
        ).slice(0, 10); // Limit to 10 results
        
        if (matches.length > 0) {
            suggestionsDiv.innerHTML = matches.map(name => 
                `<div class="suggestion-item" data-name="${name}">${name}</div>`
            ).join('');
            suggestionsDiv.style.display = 'block';
        } else {
            suggestionsDiv.style.display = 'none';
        }
    });
    
    // Handle suggestion clicks
    suggestionsDiv.addEventListener('click', function(e) {
        if (e.target.classList.contains('suggestion-item')) {
            const playerName = e.target.getAttribute('data-name');
            searchInput.value = playerName;
            suggestionsDiv.style.display = 'none';
            showPlayerSchedule(playerName);
        }
    });
    
    // Hide suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !suggestionsDiv.contains(e.target)) {
            suggestionsDiv.style.display = 'none';
        }
    });
    
    // Handle enter key
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            const suggestions = suggestionsDiv.querySelectorAll('.suggestion-item');
            if (suggestions.length > 0) {
                const playerName = suggestions[0].getAttribute('data-name');
                searchInput.value = playerName;
                suggestionsDiv.style.display = 'none';
                showPlayerSchedule(playerName);
            }
        }
    });
}

function showPlayerSchedule(playerName) {
    const mainSchedule = getPlayerSchedule(playerName);
    const teamSchedule = getTeamPlayerSchedule(playerName);
    const player = TOURNAMENT_DATA.playersByName.get(playerName);
    
    if (!player || (mainSchedule.length === 0 && teamSchedule.length === 0)) {
            document.getElementById('results').style.display = 'none';
    document.getElementById('noResults').style.display = 'block';
    document.getElementById('calendarDownload').style.display = 'none';
        return;
    }
    
    // Show permanent link
    const permanentLinkDiv = document.getElementById('permanentLink');
    const directLinkUrl = document.getElementById('directLinkUrl');
    const currentUrl = window.location.origin + window.location.pathname + '?id=' + player.id;
    directLinkUrl.href = currentUrl;
    directLinkUrl.textContent = currentUrl;
    permanentLinkDiv.style.display = 'block';
    
    // Show player info
    const playerInfoDiv = document.getElementById('playerInfo');
    playerInfoDiv.innerHTML = `
        <h2 class="selected-player">${player.name}<span class="country">
            (${player.country})
        </span></h2>
    `;
    
    // Show team event schedule if player participates
    const teamEventSection = document.getElementById('teamEventSection');
    const teamRoundsContainer = document.getElementById('teamRoundsContainer');
    
    if (teamSchedule.length > 0) {
        teamRoundsContainer.innerHTML = teamSchedule.map(roundInfo => {
            const schedule = SCHEDULE_DATA.teamEvent[roundInfo.round];
            const scheduleText = schedule ?
                ` <span class="schedule">${schedule.day} ${schedule.time}</span>` 
                : '';
            return `
            <div class="round-card">
                <div class="round-header">
                    Round ${roundInfo.round} - Table <b>${roundInfo.table}</b>${scheduleText}
                </div>
                <div>
                    <ul class="tablemates">
                        ${roundInfo.tablemates.map(mate => `
                            <li class="tablemate">
                                ${mate.name}
                                <span class="country">(${mate.teamName})</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            </div>
        `}).join('');
        teamEventSection.style.display = 'block';
    } else {
        teamEventSection.style.display = 'none';
    }
    
    // Show main event schedule
    const mainEventSection = document.getElementById('mainEventSection');
    const mainRoundsContainer = document.getElementById('mainRoundsContainer');
    
    if (mainSchedule.length > 0) {
        mainRoundsContainer.innerHTML = mainSchedule.map(roundInfo => {
            const schedule = SCHEDULE_DATA.mainEvent[roundInfo.round];
            const scheduleText = schedule ? 
                ` <span class="schedule">${schedule.day} ${schedule.time}</span>` 
                : '';
            return `
            <div class="round-card">
                <div class="round-header">
                    Round ${roundInfo.round} - Table <b>${roundInfo.table}</b>${scheduleText}
                </div>
                <div>
                    <ul class="tablemates">
                        ${roundInfo.tablemates.map(mate => `
                            <li class="tablemate">
                                ${mate.name}
                                <span class="country">(${mate.country})</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            </div>
        `}).join('');
        mainEventSection.style.display = 'block';
    } else {
        mainEventSection.style.display = 'none';
    }
    
    document.getElementById('results').style.display = 'block';
    document.getElementById('noResults').style.display = 'none';
    
    // Show calendar download option
    const calendarDownload = document.getElementById('calendarDownload');
    calendarDownload.style.display = 'block';
    
    // Set up download button
    const downloadButton = document.getElementById('downloadButton');
    downloadButton.onclick = () => generatePersonalCalendar(player, teamSchedule, mainSchedule);
}

// Function to handle direct links with player ID
function handleDirectLink() {
    const playerId = getUrlParameter('id');
    if (playerId) {
        const playerName = getPlayerNameById(playerId);
        if (playerName) {
            const searchInput = document.getElementById('playerSearch');
            searchInput.value = playerName;
            showPlayerSchedule(playerName);
        }
    }
}

// Function to generate personalized calendar file
function generatePersonalCalendar(player, teamSchedule, mainSchedule) {
    const playerName = player.name.replace(/[^a-zA-Z0-9]/g, '_');
    const filename = `WRC2025_${playerName}_Calendar.ics`;
    const includeNotifications = document.getElementById('includeNotifications').checked;
    
    let icsContent = `BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
METHOD:PUBLISH
PRODID:-//WRC//Personal Calendar for ${player.name}//EN
X-WR-TIMEZONE:Asia/Tokyo
BEGIN:VTIMEZONE
TZID:Asia/Tokyo
X-LIC-LOCATION:Asia/Tokyo
BEGIN:STANDARD
TZOFFSETFROM:+0900
TZOFFSETTO:+0900
TZNAME:JST
DTSTART:19700101T000000
END:STANDARD
END:VTIMEZONE

`;

    // Add team event rounds
    teamSchedule.forEach(roundInfo => {
        const schedule = SCHEDULE_DATA.teamEvent[roundInfo.round];
        if (schedule) {
            const tablemates = roundInfo.tablemates.map(mate => `${mate.name} (${mate.teamName})`).join(', ');
            const description = tablemates ? `Other players at this table: ${tablemates}` : 'Other players not found';
            
            icsContent += `BEGIN:VEVENT
DTSTART;TZID=Asia/Tokyo:${schedule.date.replace(/-/g, '')}T${schedule.time.replace(':', '')}00
DTEND;TZID=Asia/Tokyo:${schedule.date.replace(/-/g, '')}T${addMinutes(schedule.time, 70)}00
SUMMARY:Team Round ${roundInfo.round} Table ${roundInfo.table}
DESCRIPTION:${description}
LOCATION:5th floor, Nihonbashi Mitsui Hall, 5F COREDO Muromachi 1, 2-2-1 Nihonbashi Muromachi, Chuo-ku, Tokyo, Japan`;

            if (includeNotifications) {
                icsContent += `
BEGIN:VALARM
TRIGGER:-PT5M
ACTION:DISPLAY
DESCRIPTION:Reminder: Team Round ${roundInfo.round} starts in 5 minutes (Table ${roundInfo.table})
END:VALARM`;
            }

            icsContent += `
END:VEVENT

`;
        }
    });

    // Add main event rounds
    mainSchedule.forEach(roundInfo => {
        const schedule = SCHEDULE_DATA.mainEvent[roundInfo.round];
        if (schedule) {
            const tablemates = roundInfo.tablemates.map(mate => `${mate.name} (${mate.country})`).join(', ');
            const description = tablemates ? `Tablemates: ${tablemates}` : 'No tablemates found';
            
            icsContent += `BEGIN:VEVENT
DTSTART;TZID=Asia/Tokyo:${schedule.date.replace(/-/g, '')}T${schedule.time.replace(':', '')}00
DTEND;TZID=Asia/Tokyo:${schedule.date.replace(/-/g, '')}T${addMinutes(schedule.time, 70)}00
SUMMARY:Main Round ${roundInfo.round} Table ${roundInfo.table}
DESCRIPTION:${description}
LOCATION:5th floor, Nihonbashi Mitsui Hall, 5F COREDO Muromachi 1, 2-2-1 Nihonbashi Muromachi, Chuo-ku, Tokyo, Japan`;

            if (includeNotifications) {
                icsContent += `
BEGIN:VALARM
TRIGGER:-PT5M
ACTION:DISPLAY
DESCRIPTION:Reminder: Main Round ${roundInfo.round} starts in 5 minutes (Table ${roundInfo.table})
END:VALARM`;
            }

            icsContent += `
END:VEVENT

`;
        }
    });

    icsContent += `END:VCALENDAR`;

    // Create and download the file
    const blob = new Blob([icsContent], { type: 'text/calendar;charset=utf-8' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);
}

// Helper function to add minutes to a time string (HH:MM format)
function addMinutes(timeString, minutes) {
    const [hours, mins] = timeString.split(':').map(Number);
    const totalMinutes = hours * 60 + mins + minutes;
    const newHours = Math.floor(totalMinutes / 60) % 24;
    const newMins = totalMinutes % 60;
    return `${newHours.toString().padStart(2, '0')}${newMins.toString().padStart(2, '0')}`;
}

// Initialize data when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeTournamentData();
    setupTypeahead();
    handleDirectLink();
});
