/**
 * Client-side Progress API helper
 * Exposes: getTopics(courseId), getEnrollment(courseId), updateProgress(courseId, topicId)
 * All calls use same-origin and include credentials.
 */
window.ProgressAPI = {
    async getTopics(courseId){
        const resp = await fetch(`/api/progress/topics/${courseId}`, {
            credentials: 'same-origin'
        });
        if (!resp.ok) throw new Error('Failed to fetch topics');
        return resp.json();
    },

    async getEnrollment(courseId){
        const resp = await fetch(`/api/progress/enrollment/${courseId}`, {
            credentials: 'same-origin'
        });
        if (!resp.ok) throw new Error('Failed to fetch enrollment');
        return resp.json();
    },

    async updateProgress(courseId, topicId){
        const resp = await fetch(`/api/progress/update/${courseId}/${topicId}`, {
            method: 'PUT',
            credentials: 'same-origin'
        });
        if (!resp.ok) throw new Error('Failed to update progress');
        return resp.json();
    }
};
