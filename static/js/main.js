// Base Logic
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('access_token');
    const authButtons = document.querySelector('.auth-buttons');
    
    if (authButtons && token) {
        authButtons.innerHTML = `
            <a href="/dashboard" class="btn btn-outline">My Account</a>
            <button onclick="logout()" class="btn btn-primary">Log Out</button>
        `;
    }
});

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
}

// Home & Courses Logic
async function fetchCourses(elementId, limit = null) {
    const grid = document.getElementById(elementId);
    if (!grid) return;
    
    try {
        const response = await fetch('/api/courses/courses/');
        let courses = await response.json();
        
        if (courses.length === 0) {
            grid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: var(--text-muted);">No courses available yet.</p>';
            return;
        }

        if (limit) courses = courses.slice(0, limit);

        courses.forEach(course => {
            const card = document.createElement('div');
            card.className = 'glass-container course-card animate-fade-in';
            card.innerHTML = `
                <img src="${course.thumbnail || 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'}" alt="${course.title}" class="course-img">
                <div style="padding: 0.5rem 0;">
                    <span style="font-size: 0.8rem; background: rgba(205, 155, 89, 0.2); color: var(--primary); padding: 0.2rem 0.6rem; border-radius: 4px;">${course.category_name || 'General'}</span>
                </div>
                <h3 class="course-title">${course.title}</h3>
                <p style="color: var(--text-muted); font-size: 0.9rem;">${course.description.substring(0, 100)}...</p>
                <div class="course-meta">
                    <span>Instructor: ${course.instructor_name || 'Expert'}</span>
                </div>
                <div class="course-meta" style="margin-top: auto; align-items: center;">
                    <span class="course-price">$${course.price}</span>
                    ${limit ? `<a href="/courses/${course.id}" class="btn btn-outline" style="padding: 0.4rem 1rem;">View Details</a>` : `<button onclick="enroll(${course.id})" class="btn btn-primary" style="padding: 0.4rem 1rem;">Enroll Now</button>`}
                </div>
            `;
            grid.appendChild(card);
        });
    } catch (error) {
        console.error('Error fetching courses:', error);
        grid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: var(--text-muted);">Failed to load courses.</p>';
    }
}

async function enroll(courseId) {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login';
        return;
    }

    try {
        const response = await fetch('/api/payments/checkout/', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ course_id: courseId })
        });

        if (response.ok) {
            alert('Successfully enrolled!');
            window.location.href = '/dashboard';
        } else {
            alert('Failed to enroll. You might already be enrolled.');
        }
    } catch (err) {
        alert('An error occurred during enrollment.');
    }
}

// Dashboard Logic
async function loadDashboard() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login';
        return;
    }

    try {
        const response = await fetch('/api/dashboard/student/', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            
            document.getElementById('dashboard-stats').innerHTML = `
                <div style="background: rgba(202, 237, 184, 0.5); padding: 1.5rem; border-radius: 12px; flex: 1;">
                    <h4 style="color: var(--ebony); margin-bottom: 0.5rem;">Enrolled Courses</h4>
                    <p style="font-size: 2rem; font-weight: bold; color: var(--chestnut);">${data.total_enrolled}</p>
                </div>
                <div style="background: rgba(150, 63, 46, 0.1); padding: 1.5rem; border-radius: 12px; flex: 1;">
                    <h4 style="color: var(--ebony); margin-bottom: 0.5rem;">Completed</h4>
                    <p style="font-size: 2rem; font-weight: bold; color: var(--chestnut);">${data.completed_courses}</p>
                </div>
            `;

            const coursesGrid = document.getElementById('my-courses');
            if (data.learning_progress.length === 0) {
                coursesGrid.innerHTML = '<p style="color: var(--text-muted);">You have not enrolled in any courses yet.</p>';
            } else {
                coursesGrid.innerHTML = '';
                data.learning_progress.forEach(item => {
                    const card = document.createElement('div');
                    card.className = 'glass-container course-card animate-fade-in';
                    card.style.padding = '1.5rem';
                    card.innerHTML = `
                        <h4 style="font-size: 1.2rem; margin-bottom: 1rem;">${item.course}</h4>
                        <div style="background: rgba(255,255,255,0.1); height: 8px; border-radius: 4px; overflow: hidden; margin-bottom: 0.5rem;">
                            <div style="width: ${item.progress}%; background: var(--primary); height: 100%;"></div>
                        </div>
                        <p style="text-align: right; font-size: 0.9rem; color: var(--text-muted);">${item.progress}% Completed</p>
                    `;
                    coursesGrid.appendChild(card);
                });
            }

            // Render Announcements
            const announcementsList = document.getElementById('announcements-list');
            if (data.announcements && data.announcements.length > 0) {
                announcementsList.innerHTML = data.announcements.map(a => `
                    <div style="background: rgba(0,0,0,0.02); padding: 1rem; border-radius: 8px; border-left: 4px solid var(--chestnut);">
                        <p style="font-size: 0.8rem; color: var(--primary); margin-bottom: 0.3rem;">${a.course}</p>
                        <h5 style="margin-bottom: 0.3rem; color: var(--ebony);">${a.title}</h5>
                        <p style="font-size: 0.9rem; color: var(--text-muted);">${a.content}</p>
                        <span style="font-size: 0.75rem; color: var(--text-muted); display: block; margin-top: 0.5rem;">${new Date(a.date).toLocaleDateString()}</span>
                    </div>
                `).join('');
            } else {
                announcementsList.innerHTML = '<p style="color: var(--text-muted); font-size: 0.9rem;">No recent announcements.</p>';
            }

            // Render Recent Lessons
            const recentLessonsDiv = document.getElementById('recent-lessons');
            if (data.recent_lessons && data.recent_lessons.length > 0) {
                recentLessonsDiv.innerHTML = data.recent_lessons.map(l => `
                    <a href="/lessons/${l.id}/" style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 8px; border: 1px solid var(--border-color); text-decoration: none; color: inherit; transition: background 0.3s;">
                        <div>
                            <p style="font-size: 0.8rem; color: var(--primary); margin-bottom: 0.2rem;">${l.course}</p>
                            <h5 style="font-size: 1rem; color: var(--ebony); margin: 0;">${l.title}</h5>
                        </div>
                        <span class="btn btn-outline" style="padding: 0.3rem 1rem; font-size: 0.8rem;">Watch</span>
                    </a>
                `).join('');
            } else {
                recentLessonsDiv.innerHTML = '<p style="color: var(--text-muted);">No recent lessons.</p>';
            }

            // Render Recommended Courses
            const recommendedGrid = document.getElementById('recommended-courses');
            if (data.recommended_courses && data.recommended_courses.length > 0) {
                recommendedGrid.innerHTML = data.recommended_courses.map(c => `
                    <div class="glass-container course-card animate-fade-in" style="padding: 1rem;">
                        <h4 style="font-size: 1.1rem; margin-bottom: 0.5rem; color: var(--ebony);">${c.title}</h4>
                        <p style="color: var(--text-muted); margin-bottom: 1rem; font-size: 0.9rem;">$${c.price}</p>
                        <a href="/courses/${c.slug}" class="btn btn-outline" style="width: 100%; text-align: center; padding: 0.5rem;">View Course</a>
                    </div>
                `).join('');
            } else {
                recommendedGrid.innerHTML = '<p style="color: var(--text-muted);">No recommendations at this time.</p>';
            }

        } else if (response.status === 401 || response.status === 403) {
            localStorage.removeItem('access_token');
            window.location.href = '/login';
        }
    } catch (err) {
        console.error('Failed to load dashboard:', err);
    }
}
