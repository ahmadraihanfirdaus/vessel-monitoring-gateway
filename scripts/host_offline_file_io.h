/* Shared actual host-file callbacks, NOT ESP32/NVS durability proof. */
#ifndef VG_HOST_OFFLINE_FILE_IO_H
#define VG_HOST_OFFLINE_FILE_IO_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <errno.h>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#else
#include <unistd.h>
#endif
typedef struct { char paths[2][1024]; FILE *pending; } file_disk;
static vg_offline_read_result file_read(void *context,unsigned slot,uint8_t *out,size_t cap,size_t *length)
{
    file_disk *d=context;if(slot>1u)return VG_OFFLINE_READ_ERROR;
    FILE *file=fopen(d->paths[slot],"rb");
    if(!file)return errno==ENOENT?VG_OFFLINE_READ_ABSENT:VG_OFFLINE_READ_ERROR;
    *length=fread(out,1u,cap,file);
    bool valid=!ferror(file) && fgetc(file)==EOF && *length>0u;
    if(fclose(file)!=0)valid=false;
    return valid?VG_OFFLINE_READ_READY:VG_OFFLINE_READ_ERROR;
}
static bool file_write(void *context,unsigned slot,const uint8_t *raw,size_t length)
{
    file_disk *d=context;
    if(slot>1u || d->pending || !length || length>VG_OFFLINE_SNAPSHOT_MAX)return false;
    d->pending=fopen(d->paths[slot],"wb");
    return d->pending && fwrite(raw,1u,length,d->pending)==length && fflush(d->pending)==0;
}
static bool file_commit(void *context)
{
    file_disk *d=context;if(!d->pending)return false;
#ifdef _WIN32
    bool valid=_commit(_fileno(d->pending))==0;
#else
    bool valid=fsync(fileno(d->pending))==0;
#endif
    if(fclose(d->pending)!=0)valid=false;
    d->pending=NULL;return valid;
}
#endif
