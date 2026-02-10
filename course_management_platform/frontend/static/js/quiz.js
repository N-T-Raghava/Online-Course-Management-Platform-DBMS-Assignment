/**
 * Quiz API Service
 * Handles all quiz-related API calls from frontend
 */

class QuizAPI {
    constructor(baseUrl = 'http://127.0.0.1:8000') {
        this.baseUrl = baseUrl;
    }

    /**
     * Fetch quiz and questions for a specific course
     * @param {number} courseId - Course ID
     * @param {string} token - Auth token (optional)
     * @returns {Promise<Object>} Quiz data with questions
     */
    async getQuizForCourse(courseId, token = null) {
        try {
            const headers = {};
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }

            const response = await fetch(
                `${this.baseUrl}/quizzes/course/${courseId}`,
                { 
                    method: 'GET',
                    headers: headers
                }
            );

            if (!response.ok) {
                throw new Error(`Failed to fetch quiz: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error fetching quiz:', error);
            throw error;
        }
    }

    /**
     * Fetch all questions for a quiz
     * @param {number} quizId - Quiz ID
     * @param {string} token - Auth token (optional)
     * @returns {Promise<Object>} Quiz with questions array
     */
    async getQuizQuestions(quizId, token = null) {
        try {
            const headers = {};
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }

            const response = await fetch(
                `${this.baseUrl}/quizzes/${quizId}/questions`,
                { 
                    method: 'GET',
                    headers: headers
                }
            );

            if (!response.ok) {
                throw new Error(`Failed to fetch questions: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error fetching questions:', error);
            throw error;
        }
    }

    /**
     * Add a new question to a quiz
     * @param {number} quizId - Quiz ID
     * @param {Object} questionData - Question data
     * @param {string} token - Auth token
     * @returns {Promise<Object>} Created question
     */
    async addQuestion(quizId, questionData, token) {
        try {
            const response = await fetch(
                `${this.baseUrl}/quizzes/${quizId}/questions`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(questionData)
                }
            );

            if (!response.ok) {
                throw new Error(`Failed to add question: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error adding question:', error);
            throw error;
        }
    }

    /**
     * Delete a question from a quiz
     * @param {number} questionId - Question ID
     * @param {string} token - Auth token
     * @returns {Promise<Object>} Success response
     */
    async deleteQuestion(questionId, token) {
        try {
            const response = await fetch(
                `${this.baseUrl}/quizzes/questions/${questionId}`,
                {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                }
            );

            if (!response.ok) {
                throw new Error(`Failed to delete question: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error deleting question:', error);
            throw error;
        }
    }

    /**
     * Update the answer key for a course
     * @param {number} courseId - Course ID
     * @param {string} answerKey - Answer key string (e.g., "ABCABC...")
     * @param {string} token - Auth token
     * @returns {Promise<Object>} Updated course data
     */
    async updateAnswerKey(courseId, answerKey, token) {
        try {
            const response = await fetch(
                `${this.baseUrl}/quizzes/courses/${courseId}/answer-key`,
                {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({ answer_key: answerKey })
                }
            );

            if (!response.ok) {
                throw new Error(`Failed to update answer key: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error updating answer key:', error);
            throw error;
        }
    }
}

// Initialize global quiz API instance
window.QuizAPI = new QuizAPI();

/**
 * Render quiz questions dynamically in the form
 * @param {Object} quizData - Quiz data with questions array
 * @param {HTMLElement} formElement - Form element to render into
 */
async function renderQuizQuestions(quizData, formElement) {
    try {
        // Validate formElement
        if (!formElement) {
            throw new Error('Form element not found. Unable to render quiz questions.');
        }

        // Clear existing questions
        const existingQuestions = formElement.querySelectorAll('.question-card');
        existingQuestions.forEach(el => el.remove());

        // Get questions sorted by order
        const questions = quizData.questions || [];
        questions.sort((a, b) => (a.order || 0) - (b.order || 0));

        if (questions.length === 0) {
            const noQuestionsDiv = document.createElement('div');
            noQuestionsDiv.className = 'alert alert-warning';
            noQuestionsDiv.textContent = 'No questions found for this quiz.';
            formElement.appendChild(noQuestionsDiv);
            return;
        }

        // Validate questions before rendering
        const invalidQuestions = [];
        questions.forEach((q, idx) => {
            if (!q.question_id) invalidQuestions.push(`Q${idx + 1}: Missing question_id`);
            if (!q.question_text) invalidQuestions.push(`Q${idx + 1}: Missing question_text`);
            if (!q.correct_answer) invalidQuestions.push(`Q${idx + 1}: Missing correct_answer`);
            if (!q.option_a && !q.option_b && !q.option_c && !q.option_d) {
                invalidQuestions.push(`Q${idx + 1}: No answer options`);
            }
        });

        if (invalidQuestions.length > 0) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'alert alert-danger';
            errorDiv.innerHTML = '<strong>Error loading quiz:</strong><br>' + 
                invalidQuestions.map(msg => escapeHtml(msg)).join('<br>');
            formElement.appendChild(errorDiv);
            console.error('Quiz validation errors:', invalidQuestions);
            throw new Error('Quiz data validation failed');
        }

        // Render each question
        questions.forEach((question, index) => {
            const questionDiv = document.createElement('div');
            questionDiv.className = 'question-card';
            questionDiv.setAttribute('data-question-id', question.question_id);

            // Build question text
            let questionHTML = `
                <div>
                    <span class="question-number">Q${index + 1}.</span>
                    <span>${escapeHtml(question.question_text)}</span>
                </div>
                <div class="options">
            `;

            // Get available options
            const options = [];
            if (question.option_a) options.push({ label: 'A', value: 'A', text: question.option_a });
            if (question.option_b) options.push({ label: 'B', value: 'B', text: question.option_b });
            if (question.option_c) options.push({ label: 'C', value: 'C', text: question.option_c });
            if (question.option_d) options.push({ label: 'D', value: 'D', text: question.option_d });

            if (options.length === 0) {
                questionHTML += '<p style="color: red;">Error: No options available for this question</p>';
            } else {
                // Render options
                options.forEach(option => {
                    questionHTML += `
                        <label class="option">
                            <input type="radio" 
                                   name="q${question.question_id}" 
                                   value="${option.value}"
                                   required>
                            <strong>${option.label}:</strong> ${escapeHtml(option.text)}
                        </label>
                    `;
                });
            }

            questionHTML += `</div>`;
            questionDiv.innerHTML = questionHTML;
            formElement.appendChild(questionDiv);
        });

        // Store question data for grading
        window.quizQuestions = questions;

    } catch (error) {
        console.error('Error rendering quiz:', error);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger';
        errorDiv.textContent = 'Failed to load quiz questions: ' + (error.message || 'Unknown error');
        
        // Only append if formElement is valid
        if (formElement) {
            formElement.appendChild(errorDiv);
        } else {
            // If formElement is null, display error in console and alert
            console.error('Cannot display quiz error: formElement is null');
            alert('Error: Unable to render quiz. Please refresh the page.');
        }
        throw error;
    }
}

/**
 * Grade quiz answers against correct answers
 * @param {Array<string>} studentAnswers - Array of student answers (A, B, C, D)
 * @param {Array<Object>} questions - Quiz questions array
 * @returns {Object} Grading result with score and details
 */
function gradeQuiz(studentAnswers, questions) {
    if (!questions || questions.length === 0) {
        throw new Error('No quiz questions found');
    }

    if (!studentAnswers || studentAnswers.length !== questions.length) {
        throw new Error(`Answer count mismatch. Expected ${questions.length}, got ${studentAnswers.length}`);
    }

    let correctCount = 0;
    const results = [];

    questions.forEach((question, index) => {
        const studentAnswer = studentAnswers[index];
        const correctAnswer = question.correct_answer;
        
        // Validate data
        if (!studentAnswer) {
            throw new Error(`Question ${index + 1}: No answer provided`);
        }
        
        if (!correctAnswer) {
            throw new Error(`Question ${index + 1}: No correct answer configured in database`);
        }

        const isCorrect = studentAnswer.toUpperCase() === correctAnswer.toUpperCase();

        if (isCorrect) {
            correctCount++;
        }

        // Build options object (ensure lowercase keys)
        const options = {};
        if (question.option_a) options['a'] = question.option_a;
        if (question.option_b) options['b'] = question.option_b;
        if (question.option_c) options['c'] = question.option_c;
        if (question.option_d) options['d'] = question.option_d;

        results.push({
            questionId: question.question_id,
            questionText: question.question_text,
            studentAnswer: studentAnswer.toUpperCase(),
            correctAnswer: correctAnswer.toUpperCase(),
            isCorrect: isCorrect,
            explanation: question.explanation || null,
            options: options
        });
    });

    const totalQuestions = questions.length;
    const percentage = Math.round((correctCount / totalQuestions) * 100);
    const passed = percentage >= 70; // Default passing score

    return {
        correctCount: correctCount,
        totalQuestions: totalQuestions,
        percentage: percentage,
        passed: passed,
        results: results
    };
}

/**
 * Display quiz results to the student
 * @param {Object} gradingResult - Result from gradeQuiz()
 * @param {HTMLElement} resultArea - Element to display results
 */
function displayQuizResults(gradingResult, resultArea) {
    // Validate resultArea
    if (!resultArea) {
        console.error('Result area element is null');
        alert('Error: Unable to display results. Please refresh the page.');
        return;
    }

    resultArea.innerHTML = '';

    // Score banner
    const scoreDiv = document.createElement('div');
    scoreDiv.id = 'scoreText';
    scoreDiv.innerHTML = `
        <h4 style="margin-bottom: 8px;">
            Your Score: <strong style="color: ${gradingResult.passed ? '#28a745' : '#dc3545'}">${gradingResult.percentage}%</strong>
        </h4>
        <p>${gradingResult.correctCount} out of ${gradingResult.totalQuestions} correct</p>
    `;
    resultArea.appendChild(scoreDiv);

    // Grade text
    const gradeDiv = document.createElement('div');
    gradeDiv.id = 'gradeText';
    const grade = mapScoreToGrade(gradingResult.correctCount);
    const status = gradingResult.passed ? '✅ PASSED' : '❌ FAILED (70% required)';
    gradeDiv.innerHTML = `<p><strong>Grade: ${grade}</strong> — ${status}</p>`;
    resultArea.appendChild(gradeDiv);

    // Completion banner if passed
    if (gradingResult.passed) {
        const completionDiv = document.createElement('div');
        completionDiv.id = 'completionBanner';
        completionDiv.className = 'alert alert-success';
        completionDiv.innerHTML = '✨ <strong>Course completed successfully!</strong> You can now review your answers below.';
        resultArea.appendChild(completionDiv);
    }

    // Answer review section
    const reviewDiv = document.createElement('div');
    reviewDiv.innerHTML = '<hr><h5>Answer Review</h5>';

    gradingResult.results.forEach((result, index) => {
        const resultItem = document.createElement('div');
        resultItem.className = result.isCorrect ? 'alert alert-success' : 'alert alert-danger';
        resultItem.style.marginBottom = '12px';

        const statusIcon = result.isCorrect ? '✓' : '✗';
        const statusText = result.isCorrect ? 'Correct' : 'Incorrect';

        // Ensure we have valid data
        const studentAnswer = result.studentAnswer || '?';
        const correctAnswer = result.correctAnswer || '?';
        const studentAnswerKey = (studentAnswer || '').toLowerCase();
        const correctAnswerKey = (correctAnswer || '').toLowerCase();

        let studentAnswerText = studentAnswerKey && result.options ? result.options[studentAnswerKey] : 'Not answered';
        let correctAnswerText = correctAnswerKey && result.options ? result.options[correctAnswerKey] : 'Not configured';

        let reviewHTML = `
            <div style="margin-bottom: 8px;">
                <strong>${statusIcon} Q${index + 1}: ${statusText}</strong>
            </div>
            <div style="margin-bottom: 8px;">
                <strong>Question:</strong> ${escapeHtml(result.questionText)}
            </div>
            <div style="margin-bottom: 8px;">
                <strong>Your Answer:</strong> ${result.studentAnswer} - ${escapeHtml(studentAnswerText)}
            </div>
            <div style="margin-bottom: 8px;">
                <strong>Correct Answer:</strong> ${result.correctAnswer} - ${escapeHtml(correctAnswerText)}
            </div>
        `;

        if (result.explanation) {
            reviewHTML += `
                <div style="margin-top: 8px; padding: 8px; background: rgba(255,255,255,0.3); border-radius: 4px;">
                    <strong>Explanation:</strong> ${escapeHtml(result.explanation)}
                </div>
            `;
        }

        resultItem.innerHTML = reviewHTML;
        reviewDiv.appendChild(resultItem);
    });

    // Append rating block if not present (some templates render static rating, others rely on JS)
    if (!document.getElementById('stars')) {
        const ratingBlock = document.createElement('div');
        ratingBlock.innerHTML = `
            <hr>
            <h5>Rate & Review</h5>
            <div>
                <label style="display: block; margin-bottom: 8px; font-weight: 500;">Your Rating:</label>
                <div id="stars" style="display:flex; gap:8px; margin-bottom: 12px;">
                    <span class="rating-star" data-value="1">☆</span>
                    <span class="rating-star" data-value="2">☆</span>
                    <span class="rating-star" data-value="3">☆</span>
                    <span class="rating-star" data-value="4">☆</span>
                    <span class="rating-star" data-value="5">☆</span>
                </div>
                <div id="rating-display" style="margin-bottom: 12px; font-weight: 500; color: #667eea;">No rating selected</div>
                <label for="reviewText" style="display: block; margin-bottom: 8px; font-weight: 500;">Your Review (optional):</label>
                <textarea id="reviewText" class="form-control" rows="3" placeholder="Share your thoughts about this course..."></textarea>
                <div class="review-actions" style="margin-top:12px; display:flex; gap:8px; align-items:center;">
                    <label><input type="checkbox" id="isPublic"> Make review public</label>
                    <button type="button" id="submitReviewBtn" class="btn btn-success">Submit Review</button>
                </div>
                <div id="reviewMsg" style="margin-top:8px;"></div>
            </div>
        `;
        resultArea.appendChild(ratingBlock);
    }

    // If a page-defined setupRatingStars exists, call it to wire up the stars
    if (typeof window.setupRatingStars === 'function') {
        try { window.setupRatingStars(); } catch (e) { console.warn('setupRatingStars threw', e); }
    }

    resultArea.appendChild(reviewDiv);
}

/**
 * Map score count to letter grade
 * @param {number} scoreCount - Number of correct answers
 * @returns {string} Letter grade (A-F)
 */
function mapScoreToGrade(scoreCount) {
    // Assuming 15 questions total
    if (scoreCount >= 13) return 'A';
    if (scoreCount >= 10) return 'B';
    if (scoreCount >= 7) return 'C';
    if (scoreCount >= 4) return 'D';
    return 'F';
}

/**
 * Escape HTML special characters
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
