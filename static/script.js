document.getElementById('resumeForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const loading = document.getElementById('loading');
    const submitBtn = document.querySelector('.btn-generate');
    
    loading.classList.remove('hidden');
    submitBtn.disabled = true;
    submitBtn.style.opacity = '0.6';
    
    const name = document.getElementById('name').value.trim();
    const surname = document.getElementById('surname').value.trim();
    
    const clientErrors = [];
    if (!name) clientErrors.push('Имя обязательно для заполнения');
    if (!surname) clientErrors.push('Фамилия обязательна для заполнения');
    
    if (clientErrors.length > 0) {
        showErrorDialog(clientErrors, 'Пожалуйста, исправьте следующие ошибки:');
        loading.classList.add('hidden');
        submitBtn.disabled = false;
        submitBtn.style.opacity = '1';
        return;
    }
    
    const photoInput = document.getElementById('photo');
    let photoBase64 = '';
    
    if (photoInput.files && photoInput.files[0]) {
        if (photoInput.files[0].size > 5 * 1024 * 1024) {
            showErrorDialog(['Фото не должно превышать 5MB'], 'Ошибка загрузки фото:');
            loading.classList.add('hidden');
            submitBtn.disabled = false;
            submitBtn.style.opacity = '1';
            return;
        }
        
        try {
            photoBase64 = await convertToBase64(photoInput.files[0]);
        } catch (error) {
            showErrorDialog(['Не удалось загрузить фото'], 'Ошибка:');
            loading.classList.add('hidden');
            submitBtn.disabled = false;
            submitBtn.style.opacity = '1';
            return;
        }
    }
    
    const formData = {
        name: name,
        surname: surname,
        experience: document.getElementById('experience').value.trim(),
        skills: document.getElementById('skills').value.trim(),
        education: document.getElementById('education').value.trim(),
        languages: document.getElementById('languages').value.trim(),
        contact: document.getElementById('contact').value.trim(),
        photo: photoBase64
    };
    
    try {
        const response = await fetch('/generate-pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const contentType = response.headers.get('content-type');
        
        if (response.ok && contentType && contentType.includes('application/pdf')) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'CV.pdf';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            showSuccessMessage('Резюме успешно создано!');
        } else {
            const errorData = await response.json();
            
            if (errorData.errors && errorData.errors.length > 0) {
                showErrorDialog(errorData.errors, errorData.message || 'Ошибка при создании резюме:');
            } else {
                showErrorDialog(['Неизвестная ошибка'], 'Что-то пошло не так:');
            }
        }
    } catch (error) {
        console.error('Network Error:', error);
        showErrorDialog(
            ['Проверьте подключение к интернету и попробуйте снова'], 
            'Сетевая ошибка:'
        );
    } finally {
        loading.classList.add('hidden');
        submitBtn.disabled = false;
        submitBtn.style.opacity = '1';
    }
});

function convertToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
    });
}

function showErrorDialog(errors, title) {
    const modal = document.createElement('div');
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100%';
    modal.style.height = '100%';
    modal.style.backgroundColor = 'rgba(0,0,0,0.5)';
    modal.style.display = 'flex';
    modal.style.alignItems = 'center';
    modal.style.justifyContent = 'center';
    modal.style.zIndex = '2000';
    
    const modalContent = document.createElement('div');
    modalContent.style.backgroundColor = 'white';
    modalContent.style.borderRadius = '12px';
    modalContent.style.padding = '24px';
    modalContent.style.maxWidth = '500px';
    modalContent.style.width = '90%';
    modalContent.style.boxShadow = '0 10px 40px rgba(0,0,0,0.2)';
    
    modalContent.innerHTML = `
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
            <div style="font-size: 32px;">⚠️</div>
            <h3 style="color: #d32f2f; margin: 0;">${title}</h3>
        </div>
        <div style="margin-bottom: 24px;">
            ${errors.map(err => `<p style="margin: 8px 0; color: #555;">• ${escapeHtml(err)}</p>`).join('')}
        </div>
        <button onclick="this.closest('div').remove()" style="
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            font-weight: 600;
        ">Понятно</button>
    `;
    
    modal.appendChild(modalContent);
    document.body.appendChild(modal);
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

function showSuccessMessage(message) {
    const toast = document.createElement('div');
    toast.style.position = 'fixed';
    toast.style.bottom = '20px';
    toast.style.right = '20px';
    toast.style.backgroundColor = '#4caf50';
    toast.style.color = 'white';
    toast.style.padding = '16px 24px';
    toast.style.borderRadius = '8px';
    toast.style.fontWeight = '600';
    toast.style.zIndex = '2000';
    toast.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
    toast.style.animation = 'slideIn 0.3s ease';
    toast.innerHTML = `✅ ${message}`;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

document.getElementById('photo').addEventListener('change', (e) => {
    const preview = document.getElementById('photoPreview');
    preview.innerHTML = '';
    
    if (e.target.files && e.target.files[0]) {
        if (e.target.files[0].size > 5 * 1024 * 1024) {
            showErrorDialog(['Фото не должно превышать 5MB'], 'Ошибка:');
            e.target.value = '';
            return;
        }
        
        const reader = new FileReader();
        reader.onload = function(ev) {
            const img = document.createElement('img');
            img.src = ev.target.result;
            preview.appendChild(img);
        };
        reader.readAsDataURL(e.target.files[0]);
    }
});

const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);