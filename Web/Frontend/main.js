import {
    fetchPhonemesCovered,
    fetchReviewStatus, 
    fetchReviewSpell, 
    fetchReviewHomoph, 
    fetchLearn, 
    fetchSpell, 
    fetchHomophones,
    submitAnswer
} from './fetch1.js';

const API_BASE = 'http://127.0.0.1:8000';
const RESOLVE_TIME = 1500;

const div = document.getElementById('app');

let lastAction = null;

const postRestartAttempts = { amount: 2};

const globalRetryAttempts = { amount: 5};
const globalRestartAttempts = { amount: 2};

const localRestartAttempts = { amount: 2};

async function allowRetry(action) { 
    lastAction = action;
    await action();

    globalRetryAttempts.amount = 5;
}


function showError(err) {
        if (err?.name === 'APIError') { 
        console.groupCollapsed('APIError');
        console.error('meta:', {
            message: err.message,
            kind: err.kind,
            retry: err.retry,
            status: err.status,
            detail: err.detail
        });
        console.error(err);
        console.groupEnd();
    } else {
        console.error(err);
    }
}


function postError(err, input, feedback, retryBtn, host, resolve, postRetryAttempts, postRestartAttempts) {
    showError(err);

    if (postRetryAttempts === 0 || postRestartAttempts.amount === 0) {
        feedback.textContent = 'The app is not responding correctly. Please exit and try again later';
        return;
    }

    if (err?.name === 'APIError' && err.retry === false) {
        feedback.textContent = "We can't process your answer (not your fault). Please RESTART the exercise";
        const restartBtn = document.createElement('button');
        restartBtn.textContent = 'Restart';
        restartBtn.disabled = true;
        host.append(restartBtn);
        
        restartBtn.addEventListener('click', () => {
            resolve();
            div.replaceChildren();
            begin(div);
        })
        return;
    }

    input.focus();
    feedback.textContent = "We can't process your answer (not your fault). Click CHECK again in 1 second";

    setTimeout(() => retryBtn.disabled = false, 1000)
}


function getError(err, container, retryAttempts, retryAction, scope) {
    container.replaceChildren();
    const errMsg = document.createElement('h2');
    errMsg.textContent = `Something went wrong`;
    container.append(errMsg);

    showError(err);

    const restartAttempts = 
        scope === 'global'
            ? globalRestartAttempts
            : localRestartAttempts;

    const retry = err?.name === 'APIError' && err.retry === true && typeof retryAction === 'function';
    
    if (retry) {
        const btn = document.createElement('button');
        btn.textContent = 'Retry';
        btn.disabled = retryAttempts.amount <= 0;

        btn.addEventListener('click', async () => {
            if (retryAttempts.amount <= 0) return;
            retryAttempts.amount -= 1;

            container.replaceChildren();
            try {
                await retryAction(); 
            } catch (err) {
                getErrorGeneral(err, container, retryAttempts, retryAction, scope);
            }
        });
        container.append(btn);
    } else {
        const btn = document.createElement('button');
        btn.textContent = 'Restart';
        btn.disabled = restartAttempts.amount <= 0;

        btn.addEventListener('click', () => {
            if (restartAttempts.amount <= 0) return;
            restartAttempts.amount -= 1;

            div.replaceChildren();
            begin(div);
        });
        container.append(btn);
    }

    if (retryAttempts.amount <= 0 || restartAttempts.amount <= 0) {
        const feedback = document.createElement('div');
        feedback.textContent =  'The app is not responding correctly. Please exit and try again later';
        feedback.className = 'feedback';
        container.append(feedback);
        return;
    }
}

function begin(div) {
    const h1 = document.createElement('h1');
    h1.textContent = 'Welcome to the English Pronunciation Trainer';

    const btn = document.createElement('button');
    btn.textContent = 'Click to start';

    div.append(h1, btn);

    btn.addEventListener('click', async () => {
        try {
            await allowRetry(async () => {
                div.replaceChildren();
                const reviewStatus = await fetchReviewStatus();
                
                await reviewCheck(reviewStatus, div);
            });
        } catch (err) {
            getError(err, div, globalRetryAttempts, lastAction, 'global');
        }
    });
}

async function review(div) {
    return new Promise((resolve) => {            
        const btn = document.createElement('button');
        btn.textContent = 'Start';
        div.append(btn);

        btn.addEventListener('click', async () => {
            try {
                await allowRetry(async () => {
                    div.replaceChildren();
                    const phonemesCovered = await fetchPhonemesCovered();

                    const words = await fetchReviewSpell();

                    const heading = document.createElement('h2');
                    heading.textContent = 'Phonemes covered so far';
                    heading.style.color = 'rgb(255, 132, 0)';

                    const phonemes = document.createElement('ol');
                    phonemes.className = 'steps';

                    for (const phoneme of phonemesCovered) {
                        const li = document.createElement('li');
                        li.textContent = `/${phoneme.phoneme}/   `;
                        const audioBtn = playAudio(phoneme);
                        li.append(audioBtn);
                        phonemes.append(li);
                    }

                    div.append(heading, phonemes);

                    await spell(words, div, {reviewRound: true, onDone: resolve});  
                });
                
            } catch(err) {
                getError(err, div, globalRetryAttempts, lastAction, 'global'); 
            }
        });
    });
}


async function reviewCheck(reviewStatus, div) {   
    const reviewMsg = document.createElement('h2');
    const bye = document.createElement('p');
    div.append(reviewMsg);

    const btn = document.createElement('button');
    btn.textContent = 'Learn new phoneme';

    btn.addEventListener('click', () => {
        learn(div).catch(getError); 
    });

    if (!reviewStatus) {
    reviewMsg.textContent = 'Review data unavailable';
    div.append(btn);
    return;
    } 

    if (reviewStatus['status'] === 'review_only') {
    reviewMsg.textContent = 'No new sounds to learn. We can only review previously studied ones';
    await review(div);
    bye.className = 'general';
    bye.textContent = 'See you soon for another review!';
    div.append(bye);
    return;
    } 

    if (reviewStatus['status'] === 'no_progress') {
        reviewMsg.textContent = 'Enjoy your first lesson!';  
        setTimeout(async () => {
            try {
                await allowRetry(async () => {
                    await learn(div);
                });
            } catch(err) {
                getError(err, div, globalRetryAttempts, lastAction, 'global');
            }
        }, 1500);
        return;
    } 
    
    reviewMsg.textContent = 'Ready to start the review?';
    await review(div);
    div.append(btn);
    return;
}



async function learn(div) { 
    div.replaceChildren();

    const phoneme = await fetchLearn();
    
    const intro = document.createElement('h2');
    intro.style.color = 'rgb(138, 0, 231)';
    intro.textContent = `New phoneme = /${phoneme['phoneme']}/  `;

    const audioBtn = playAudio(phoneme);

    intro.append(audioBtn);
    
    const introPatterns = document.createElement('h3');
    introPatterns.textContent = 'The most common spelling patterns for this phoneme are:';
    
    div.append(intro, introPatterns);

    const patterns = Object.keys(phoneme.patterns);

    const ul = document.createElement('ul');
    ul.className = 'patterns';

    patterns.forEach(pattern => {
        const pat = document.createElement('li');
        pat.textContent = `${pattern.toUpperCase()} => ${phoneme.patterns[pattern].join(', ')}`;
        ul.append(pat);
    });
    
    const exerciseBtn = document.createElement('button');
    exerciseBtn.textContent = 'Start exercises';
    div.append(ul, exerciseBtn);

    exerciseBtn.addEventListener('click', async () => {
        exerciseBtn.remove();
        try {
            await allowRetry(async () => {
                const wordsToTest = await fetchSpell(phoneme.phoneme); 
                await spell(wordsToTest, div, {phoneme: phoneme}); 
            });
        } catch(err) {
            getError(err, div, globalRetryAttempts, lastAction, 'global');
        }
    });
}


function playAudio(phoneme) {               
    const btn = document.createElement('button');
    
    if (!phoneme.audio_url) {
        btn.textContent = 'Audio unavailable';
        btn.disabled = true;
        return btn;
    }

    const audio = new Audio(`${API_BASE}${phoneme.audio_url}`);
    btn.textContent = '▶️';

    audio.onended = () => {
        btn.disabled = false;
    };

    audio.onerror = (err) => {
        btn.textContent = '❌ Audio failed';
        console.error('Audio playback failed', err);
        btn.disabled = false;
    };

    btn.addEventListener('click', async () => {
        btn.disabled = true;
        try {
            await audio.play();      
        } catch(err) {
            btn.textContent = '❌ Audio failed';
            btn.disabled = false;
            console.error('Audio playback failed', err);
        }
    });
    return btn;
}

function createInput(attempts) {
    const input = document.createElement('input');
    input.type = 'text';
    input.placeholder = 'Enter spelling here';

    const btn = document.createElement('button');
    btn.textContent = 'Check';

    const feedback = document.createElement('div');
    feedback.textContent =  `${attempts} attempts left`;
    feedback.className = 'feedback';
    feedback.setAttribute('role', 'status');

    return {input, btn, feedback}
}


async function spell(words, div, {reviewRound = false, phoneme = null, onDone = null} = {}) {
    let index = 0;
    let retry = [];

    if (!reviewRound) {
        const warning = document.createElement('p');
        warning.textContent = 'Some of the following words may not be spelt with the common patterns above';
        warning.className = 'warning';
        div.append(warning);
    }

    const host = document.createElement('div');
    div.append(host);

    for (const word of words) {
        index ++;
        await testNoHelp(word, retry, index, host);
    }
    
    if (retry.length > 0) {
        for (const word of retry) {
            await testHelp(word, host);
        }
    }

    const homophBtn = document.createElement('button');
    homophBtn.textContent = 'Click for the next exercise';

    host.append(homophBtn);

    homophBtn.addEventListener('click', async() => {
        const localRetryAttempts = { amount: 5};

        const retryAction = async () => {
            host.replaceChildren();

            if (!reviewRound) {
                const homophsToTest = await fetchHomophones(phoneme.phoneme);
                await homophones(homophsToTest, div, host);
                return;
            }

            const homophsToReview = await fetchReviewHomoph();
            await homophones(homophsToReview, div, host, {reviewRound: true});
            const done = document.createElement('p');
            done.className = 'general';
            done.textContent = 'Review completed!';
            host.append(done);

            if (onDone) onDone()
        };
        
        try {
            await retryAction();
        } catch(err) {
            getErrorGeneral(err, host, localRetryAttempts, retryAction, 'local');
        }          
    });
}


async function testNoHelp(word, retry, index, host) {
    host.replaceChildren();

    const question = document.createElement('h3');
    const start = document.createTextNode(`${index}. How do you spell `);
    const target = document.createElement('span');
    target.textContent = word.word;
    target.className = 'test';
    const end = document.createTextNode('?');
    question.append(start, target, end);

    const {input, btn, feedback} = createInput(5);

    host.append(question, input, btn, feedback);

    await new Promise((resolve) => {
        let pending = false;
        
        let postRetryAttempts = 5;

        btn.addEventListener('click', async() => {
            if (pending) return;

            const answer = input.value.trim().toLowerCase();
            if (!answer) {
                input.focus();
                return;
            }

            const idempotencyKey = crypto.randomUUID();

            pending = true;
            btn.disabled = true;   

            try {
                const check = await submitAnswer(word.test_id, answer, 'checkSpellAnswer', idempotencyKey);
                
                if (check.answered === 'correct') {
                    input.disabled = true;
                    feedback.textContent = 'Correct! ✅';
                    setTimeout(resolve, RESOLVE_TIME);
                    return;
                } 
                
                if (check.answered === 'incorrect') {
                    pending = false;
                    btn.disabled = false;
                    input.value = '';
                    input.focus();
                    feedback.textContent = `Try again. ${check.attempts_left} attempts left`;
                    return;
                } 
                
                input.disabled = true;
                feedback.textContent = 'Incorrect. We will practise this word again later';
                retry.push(word);
                setTimeout(resolve, RESOLVE_TIME);
                return;
            } catch(err) {
                pending = false;

                const restart = err?.name === 'APIError' && err.retry === false;

                restart ? postRestartAttempts.amount-- : postRetryAttempts--;
                
                postError(err, input, feedback, btn, host, resolve, postRetryAttempts, postRestartAttempts);
            }
        });
    });
}



async function testHelp(word, host) {
    host.replaceChildren();

    const question = document.createElement('h3');
    question.textContent = 'Choose the correct spelling out of these three options';

    const spell = document.createElement('p');
    spell.textContent = word.word;
    spell.className = 'test';

    const options = document.createElement('p');
    options.className = 'general';
    options.textContent = word.options.join(' - ');

    const {input, btn, feedback} = createInput(2);

    host.append(question, spell, options, input, btn, feedback);
    
    await new Promise((resolve) => {
        let pending = false;

        let postRetryAttempts = 5;

        btn.addEventListener('click', async() => {
            if (pending) return;

            const answer = input.value.trim().toLowerCase();
            if (!answer) {
                input.focus();
                return;
            }

            if (!word.options.includes(answer)) {
                feedback.textContent = 'Choose only from the given options';
                input.value = '';
                input.focus();
                return;
            }

            const idempotencyKey = crypto.randomUUID();

            pending = true; 
            btn.disabled = true;
                
            try {
                const check = await submitAnswer(word.test_id, answer, 'checkSpellAnswer', idempotencyKey);

                if (check.answered === 'correct') {
                    input.disabled = true;
                    feedback.textContent = 'Correct! ✅';
                    setTimeout(resolve, RESOLVE_TIME);
                    return;
                }
                
                if (check.answered === 'incorrect') {
                    pending = false;
                    btn.disabled = false;
                    input.value = '';
                    input.focus();
                    feedback.textContent = `Try again. ${check.attempts_left} attempts left`;
                    return;
                }

                input.disabled = true;

                const start = document.createTextNode(`Careful: the spelling of `);
                const target = document.createElement('span');
                target.textContent = word.word;
                target.classList.add('test');
                const is = document.createTextNode(' is ');
                const solution = document.createElement('span');
                solution.textContent = check.solution;
                solution.classList.add('solution');

                feedback.replaceChildren(start, target, is, solution);
                setTimeout(resolve, 2500);
                return;
            } catch(err) {
                pending = false;

                const restart = err?.name === 'APIError' && err.retry === false;

                restart ? postRestartAttempts.amount-- : postRetryAttempts--;
                
                console.log(retry, restart);
                postError(err, input, feedback, btn, host, resolve, postRetryAttempts, postRestartAttempts); 
            }
        });
    });
}

async function homophones(homophs, div, host, {reviewRound = false} = {}) {
    let index = 0;

    const warning = document.createElement('h3');
    warning.textContent = 'Find the homophones of these phoneme combinations (example: /raɪt/ => write, right, rite, wright)'
    host.append(warning);

    for (const homoph of homophs) {
        index++;
        await testHomophone(homoph, index, host);
    }
    if (!reviewRound) {
        const bye = document.createElement('p');
        bye.className = 'general';
        bye.textContent = 'Well done! Your progress has been saved. See you soon!';
        host.append(bye);
    }

}

function feedbackHomoph(btn, input, homoph, check, feedback, leftToGuess) {
    btn.remove();
    input.remove();

    const start = document.createElement('span');
    start.className = 'feedback-failed';
    start.textContent = 
    leftToGuess === 'all'
    ? 'All the homophones of '
    : 'The remaining homophones of ';

    const target = document.createElement('span');
    target.textContent = homoph.homoph;
    target.className = 'test';

    const are = document.createElement('span');
    are.className = 'feedback-failed';
    are.textContent = ' are ';

    const solutions = document.createElement('span');
    solutions.textContent = check.solution.join(', ');
    solutions.className = 'solution';
    feedback.replaceChildren(start, target, are, solutions);
}


async function testHomophone(homoph, index, host) { 
    const exercise = document.createElement('div');

    const task= document.createElement('h3');
    const ind = document.createTextNode(`${index}. `);
    const homophone = document.createElement('span');
    homophone.textContent = homoph.homoph;
    homophone.classList.add('test');
    const rest = document.createTextNode(` has ${homoph.amount} homophones`);
    task.append(ind, homophone, rest);

    const test = document.createElement('div');

    const {input, btn, feedback} = createInput(5);

    const guessed = document.createElement('ol');
    guessed.className = 'answer';

    test.append(guessed, input, btn, feedback);
    
    exercise.append(task, test);
    host.append(exercise);

    let correctAnswers = new Set();

    await new Promise((resolve) => {
        let pending = false;

        let postRetryAttempts = 5;

        btn.addEventListener('click', async() => {
            if (pending) return;

            const answer = input.value.trim().toLowerCase();

            const solution = document.createElement('li');
            solution.textContent = `${answer}  ✅`;

            if (!answer || correctAnswers.has(answer)) {
                input.focus();
                return;
            }

            const idempotencyKey = crypto.randomUUID();

            pending = true;
            btn.disabled = true;

            try {    
                const check = await submitAnswer(homoph.test_id, answer, 'checkHomophAnswer', idempotencyKey);

                if (check.answered === 'correct') {
                    pending = false;
                    btn.disabled = false;
                    correctAnswers.add(answer);
                    
                    guessed.append(solution);
                    
                    feedback.textContent = ` ${check.attempts_left} attempts left`;
                    input.value = '';
                    input.focus();
                    return;
                }

                if (check.answered === 'done') {
                    btn.remove();
                    input.remove();
                    feedback.remove();
                    guessed.append(solution);
                    resolve();
                    return;
                }
                
                if (check.answered === 'incorrect') {
                    pending = false;
                    btn.disabled = false;
                    input.value = '';
                    input.focus();
                    feedback.textContent = `Try again. ${check.attempts_left} attempts left`;
                    return;
                } 
                
                if (check.answered === 'failed_all') {
                    feedbackHomoph(btn, input, homoph, check, feedback, 'all');
                    setTimeout(resolve, RESOLVE_TIME);
                    return;
                } 
        
                feedbackHomoph(btn, input, homoph, check, feedback, 'some');
                setTimeout(resolve, RESOLVE_TIME);
                return;
            } catch(err) {
                pending = false;

                const restart = err?.name === 'APIError' && err.retry === false;

                restart ? postRestartAttempts.amount-- : postRetryAttempts--;
                
                console.log(retry, restart);
                postError(err, input, feedback, btn, host, resolve, postRetryAttempts, postRestartAttempts);
            }
        });
    });
}




async function startApp() {
    begin(div);
}

startApp()
