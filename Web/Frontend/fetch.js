const API_BASE = 'http://127.0.0.1:8000';

const ENDPOINTS = {
    phonemesCovered: '/phonemescovered',
    reviewStatus: '/reviewstatus',
    reviewSpell: '/reviewspell',
    reviewHomoph: '/reviewhomoph',
    learn: '/learn',
    spell: '/spell/',
    homophones: '/homophones/',
    checkSpellAnswer: '/checkspellanswer',
    checkHomophAnswer: '/checkhomophanswer'
};


class APIError extends Error {
    constructor(message, {status = null, kind = 'unknown', retry = false, detail = null} = {}) {  
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.kind = kind;
        this.retry = retry;
        this.detail = detail;
    }
}

const createURL = (key, path_param = '') => `${API_BASE}${ENDPOINTS[key]}${path_param}`;


async function fetchJSON(url, options= {}, timeout = 5000) {
    const controller = new AbortController(); 
    const timer = setTimeout(() => controller.abort(), timeout);

    try {
        const resp = await fetch(url, { signal: controller.signal, ...options });
        let data = null;

        const content = resp.headers.get('content-type') || '';

        if (content.includes('application/json')) {
            data = await resp.json(); 
        }                   


        if (!resp.ok) {   
            const detail = data?.detail ?? null;

            const message = detail
                ? `${resp.status} - ${detail}` 
                : `${resp.status} - ${resp.statusText}`;  
            
            const retry = resp.status >= 500 || resp.status === 429 || resp.status === 408;    
                                                                
            throw new APIError(message, {
                status: resp.status,
                kind: 'http',
                retry,
                detail
            });
        } 

        if (data === null) { 
            throw new APIError('Expected JSON from server', {kind: 'parse', retry: true});
        }

        return data;
    } catch(err) {
        if (err.name === 'AbortError') {
            throw new APIError('Request timed out', {kind: 'timeout', retry: true});
        }
        if (err instanceof TypeError) {
            throw new APIError('Network or CORS error', {kind: 'network', retry: true}); 
        }
        if (err instanceof SyntaxError) {
            throw new APIError('Invalid JSON from server', {kind: 'parse', retry: true}) 
        }
        if (err instanceof APIError) {
            throw err;  
        }
        throw err            
    } finally {
        clearTimeout(timer);
    }  
}    


async function fetchValidate({key, path_param = '', type = 'object', init}) {
    const data = await fetchJSON(createURL(key, path_param), init);

    if (type === 'array' && !Array.isArray(data)) {
        throw new APIError(`Expected array from ${key}`, {kind: 'schema', retry: false});
    }

    if (type === 'object' && (Array.isArray(data) || data === null || typeof data !== 'object')) {
        throw new APIError(`Expected dictionary from ${key}`, {kind: 'schema', retry: false});
    }
    
    return data; 
}


export const fetchPhonemesCovered = () => 
    fetchValidate({key: 'phonemesCovered', type: 'array'});


export const fetchReviewStatus = () =>
    fetchValidate({key: 'reviewStatus', type: 'object'});


export const fetchReviewSpell = () =>
    fetchValidate({key: 'reviewSpell', type: 'array'});


export const fetchReviewHomoph = () => 
    fetchValidate({key: 'reviewHomoph', type: 'array'});


export const fetchLearn = () => 
    fetchValidate({key: 'learn', type: 'object'});


export const fetchSpell = (phoneme) =>
    fetchValidate({key: 'spell', path_param : encodeURIComponent(phoneme), type: 'array'});


export const fetchHomophones = (phoneme) =>
    fetchValidate({key: 'homophones', path_param: encodeURIComponent(phoneme), type: 'array'});


export const submitAnswer = (test_id, answer, endpoint, idempotencyKey) => 
    fetchValidate({key: endpoint, type: 'object', init: {method: 'POST', 
        body: JSON.stringify({test_id, answer}),
        headers: {'Content-Type': 'application/json', 'Idempotency-Key': idempotencyKey}}})