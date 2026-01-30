phonemes = {
    'ɔ:': {
        'patterns': {
            'aw': ('saw', 'yawn', 'draw'),
            'ore': ('core', 'snore', 'before'),
            'oar': ('board', 'coarse', 'soar'),
            'or': ('port', 'absorb', 'corn'),
            'au': ('august', 'autumn', 'flaunt'),
            'oor': ('door', 'floor', 'poor'),
            'our': ('mourn', 'pour', 'four'),
            'war': ('war', 'award', 'swarm'),
        },
        'spelling': {
            "/'ɔ:də/": ('order', 'aurder', 'awder'),
            "/'kɔ:ʃən/": ('caution', 'courtion', 'coretion'),
            '/wɔ:d/': ('ward', 'word', 'woard'),
            '/lɔ:ntʃ/': ('launch', 'lunch', 'lawnch'),
            '/dɔ:n/': ('dawn', 'down', 'daun'),
            '/dʒɔ:/': ('jaw', 'jore', 'joor'),
            "/dɪ'vɔ:s/": ('divorce', 'divauce', 'divawrce'),
            "/ə'fɔ:d/": ('afford', 'affawd', 'affaud'),
            '/stɔ:/': ('store', 'stoar', 'stour'),
            '/swɔ:/': ('swore', 'swar', 'swor'),
        },
        'homophones': {
            '/ɔ:/': {'or', 'oar', 'awe', 'ore'},
            '/sɔ:/': {'saw', 'sore', 'soar'},
            '/bɔ:d/': {'bored', 'board'},
            '/flɔ:/': {'floor', 'flaw'},
            '/ʃɔ:/': {'shore', 'sure'},
            '/pɔ:/': {'poor', 'paw', 'pore', 'pour'},
            '/sɔ:s/': {'sauce', 'source'},
            "/'mɔ:nɪŋ/": {'morning', 'mourning'},
            '/stɔ:k/': {'stalk', 'stork'},
            '/wɔ:/': {'war', 'wore'},
        },
        'api': 'or'
    },
    'ɜ:': {
        'patterns': {
            'er + con': ('alert', 'deserve', 'universe'),
            'ir + con': ('girl', 'third', 'dirt'),
            'wor + con': ('word', 'work', 'worse'),
            'ur + con': ('curl', 'burden', 'lurk'),
            'ear + con': ('pearl', 'hearse', 'learn'),
        },
        'spelling': {
            '/wɜ:m/': ('worm', 'warm', 'werm'),
            '/ʃɜ:t/': ('shirt', 'shert', 'short'),
            '/bɜ:st/': ('burst', 'birst', 'berst'),
            '/pɜ:k/': ('perk', 'purk', 'pirk'),
            '/fɜ:m/': ('firm', 'furm', 'ferm'),
        },
        'homophones': {
            '/hɜ:d/': {'heard', 'herd'},
            '/fɜ:/': {'fir', 'fur'},
            '/wɜ:d/': {'word', 'whirred'},
            '/kɜ:b/': {'kerb', 'curb'},
        },
        'api': 'err'
    },
    'eə': {
        'patterns': {
            'are': ('care', 'stare', 'ware'),
            'air': ('affair', 'chair', 'repair'),
            'ear': ('swear', 'pear', 'bear'),
        },
        'spelling': {
            '/leə/': ('lair', 'lare', 'lere'),
            '/preə/': ('prayer', 'prarre', 'prair'),
            "/ˌvedʒə'teəriən/": ('vegetarian', 'vegetearian', 'vegetairian'),
            "/'peərənt/": ('parent', 'pairent', 'perent'),
            "/'veəri/": ('vary', 'very', 'veary'),
        },
        'homophones': {
            '/feə/': {'fair', 'fare'},
            '/peə/': {'pare', 'pair', 'pear'},
            '/heə/': {'hair', 'hare'},
            '/steə/': {'stare', 'stair'},
            '/fleə/': {'flair', 'flare'},
        },
        'api': 'air'
    },
    'i:': {
        'patterns': {
            'ee': ('green', 'proceed', 'tree'),
            'ie': ('believe', 'grief', 'priest'),
            'ea': ('each', 'bleak', 'dream'),
            'e.e': ('complete', 'phoneme', 'theme'),
            'i.e': ('police', 'prestige', 'unique'),
        },
        'spelling': {
            '/tʃi:t/': ('cheat', 'cheet', 'chete'),
            "/ə'tʃi:v/": ('achieve', 'acheive', 'achive'),
            '/fli:t/': ('fleet', 'fleat', 'fliet'),
            "/kən'si:t/": ('conceit', 'conciet', 'concete'),
            '/pli:/': ('plea', 'plee', 'ply'),
        },
        'homophones': {
            '/si:/': {'sea', 'see'},
            '/pi:/': {'pea', 'pee'},
            '/bi:t/': {'beet', 'beat'},
            '/bi:/': {'bee', 'be'},
            '/ri:d/':{'read', 'reed'},
            '/si:m/': {'seam', 'seem'},
            '/fli:/': {'flee', 'flea'},
        },
        'api': 'e'
    }
}
