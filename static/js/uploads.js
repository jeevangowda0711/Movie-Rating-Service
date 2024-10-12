async function fetchUserFiles() {
  const response = await fetch('/api/users/me/files', {
      headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
  });
  const data = await response.json();
  const fileList = document.getElementById('file-list');
  fileList.innerHTML = '';

  data.files.forEach(file => {
      const fileItem = document.createElement('li');
      fileItem.textContent = `${file.filename} - Uploaded on ${file.upload_date}`;
      fileList.appendChild(fileItem);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  fetchUserFiles();
});
