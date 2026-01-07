<template>
  <div class="files-page">
    <el-card shadow="hover">
      <div slot="header" class="panel-header">
        <span>文件列表</span>
        <div class="actions">
          <el-input v-model="datasetId" placeholder="datasetId" size="small" style="width:200px" />
          <el-button type="primary" size="small" @click="loadFiles" :loading="loading">加载</el-button>
        </div>
      </div>
      <el-table :data="files" v-loading="loading" height="380" border>
        <el-table-column prop="fileId" label="File ID" width="200" />
        <el-table-column prop="filename" label="文件名" />
        <el-table-column prop="size" label="大小" width="120" />
        <el-table-column prop="status" label="状态" width="120" />
        <el-table-column label="下载" width="160">
          <template slot-scope="scope">
            <el-button type="text" size="mini" @click="downloadFile(scope.row.fileId)" :loading="downloadingId === scope.row.fileId">下载</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div v-if="message" class="result" :class="{ error: isError }">{{ message }}</div>
    </el-card>
  </div>
</template>

<script>
import api from '@/api';

export default {
  name: 'FilesView',
  data() {
    return {
      datasetId: '',
      files: [],
      loading: false,
      downloadingId: null,
      message: '',
      isError: false
    };
  },
  methods: {
    async loadFiles() {
      if (!this.datasetId) return;
      this.loading = true;
      this.files = [];
      this.message = '';
      this.isError = false;
      try {
        const { data } = await api.listFiles(this.datasetId);
        this.files = data || [];
      } catch (err) {
        this.files = [];
        this.message = err?.message || '加载失败';
        this.isError = true;
      } finally {
        this.loading = false;
      }
    },
    async downloadFile(fileId) {
      this.message = '';
      this.isError = false;
      this.downloadingId = fileId;
      try {
        const { data } = await api.getDownloadUrl(fileId);
        const downloadUrl = data.url;
        
        // Trigger download by opening URL in new window or iframe
        window.open(downloadUrl, '_blank');
        this.message = '下载链接已打开';
        this.isError = false;
      } catch (err) {
        this.message = err?.message || '获取下载链接失败';
        this.isError = true;
      } finally {
        this.downloadingId = null;
      }
    }
  }
};
</script>

<style scoped>
.files-page {
  max-width: 900px;
}
.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.actions {
  display: flex;
  gap: 8px;
  align-items: center;
}
.result {
  margin-top: 10px;
  padding: 8px;
  background: rgba(56, 189, 248, 0.1);
  border-radius: 4px;
  word-break: break-all;
}
.result.error {
  background: rgba(245, 108, 108, 0.1);
  color: #f56c6c;
}
</style>
