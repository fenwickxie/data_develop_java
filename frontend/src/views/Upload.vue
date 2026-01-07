<template>
  <div class="upload-page">
    <el-card shadow="hover">
      <div slot="header" class="panel-header">
        <span>文件上传（签名 URL 流程）</span>
      </div>
      <el-form label-position="left" label-width="100px" :model="form" class="form">
        <el-form-item label="Dataset ID">
          <el-input v-model="form.datasetId" placeholder="dataset-001" />
        </el-form-item>
        <el-form-item label="File ID">
          <el-input v-model="form.fileId" placeholder="file-001" />
        </el-form-item>
        <el-form-item label="Bucket">
          <el-input v-model="form.bucket" placeholder="data-bucket" />
        </el-form-item>
        <el-form-item label="Object Key">
          <el-input v-model="form.objectKey" placeholder="path/to/file.csv" />
        </el-form-item>
        <el-form-item label="选择文件">
          <input type="file" @change="onFileChange" ref="fileInput" />
          <div v-if="selectedFile" class="file-info">
            {{ selectedFile.name }} ({{ formatSize(selectedFile.size) }})
          </div>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="uploadFlow" :loading="uploading" :disabled="!selectedFile">
            上传文件
          </el-button>
          <el-button @click="reset">重置</el-button>
        </el-form-item>
      </el-form>
      <div v-if="progress > 0" class="progress">
        <el-progress :percentage="progress" :status="progressStatus" />
      </div>
      <div v-if="message" class="result" :class="{ error: isError }">{{ message }}</div>
    </el-card>
  </div>
</template>

<script>
import api from '@/api';
import axios from 'axios';

export default {
  name: 'UploadView',
  data() {
    return {
      uploading: false,
      selectedFile: null,
      progress: 0,
      progressStatus: '',
      message: '',
      isError: false,
      form: {
        datasetId: '',
        fileId: '',
        bucket: '',
        objectKey: ''
      }
    };
  },
  methods: {
    onFileChange(event) {
      const files = event.target.files;
      if (files.length > 0) {
        this.selectedFile = files[0];
        if (!this.form.objectKey) {
          this.form.objectKey = files[0].name;
        }
      }
    },
    async uploadFlow() {
      if (!this.selectedFile) return;
      
      this.uploading = true;
      this.message = '';
      this.isError = false;
      this.progress = 10;
      this.progressStatus = '';

      try {
        // Step 1: Get signed upload URL
        this.message = '正在获取上传 URL...';
        const { data } = await api.createUploadUrl({ 
          bucket: this.form.bucket, 
          objectKey: this.form.objectKey 
        });
        const uploadUrl = data.url;
        this.progress = 30;

        // Step 2: Upload file to object storage
        this.message = '正在上传文件...';
        await axios.put(uploadUrl, this.selectedFile, {
          headers: {
            'Content-Type': this.selectedFile.type || 'application/octet-stream'
          },
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round((progressEvent.loaded * 40) / progressEvent.total) + 30;
            this.progress = Math.min(percentCompleted, 70);
          }
        });
        this.progress = 80;

        // Step 3: Register file metadata in backend
        this.message = '正在注册文件元数据...';
        await api.createFile(this.form.datasetId, {
          fileId: this.form.fileId,
          filename: this.selectedFile.name,
          bucket: this.form.bucket,
          objectKey: this.form.objectKey,
          storageType: 'OCI',
          size: this.selectedFile.size,
          contentType: this.selectedFile.type || 'application/octet-stream',
          checksum: '',
          version: '1',
          encryptFlag: false,
          status: 'UPLOADED'
        });
        
        this.progress = 100;
        this.progressStatus = 'success';
        this.message = '上传成功！';
        this.isError = false;
      } catch (err) {
        this.progress = 0;
        this.progressStatus = 'exception';
        this.isError = true;
        this.message = err?.response?.data?.message || err?.message || '上传失败';
      } finally {
        this.uploading = false;
      }
    },
    reset() {
      this.selectedFile = null;
      this.progress = 0;
      this.progressStatus = '';
      this.message = '';
      this.isError = false;
      this.form = {
        datasetId: '',
        fileId: '',
        bucket: '',
        objectKey: ''
      };
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = '';
      }
    },
    formatSize(bytes) {
      if (bytes < 1024) return bytes + ' B';
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
      return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
    }
  }
};
</script>

<style scoped>
.upload-page {
  max-width: 700px;
}
.panel-header {
  font-weight: 600;
}
.file-info {
  margin-top: 8px;
  color: #94a3b8;
  font-size: 14px;
}
.progress {
  margin: 16px 0;
}
.result {
  margin-top: 12px;
  padding: 10px;
  background: rgba(56, 189, 248, 0.1);
  border-radius: 4px;
  word-break: break-all;
}
.result.error {
  background: rgba(245, 108, 108, 0.1);
  color: #f56c6c;
}
.form {
  max-width: 600px;
}
</style>
