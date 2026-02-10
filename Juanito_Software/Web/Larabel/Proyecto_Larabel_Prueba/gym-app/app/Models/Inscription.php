<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Inscription extends Model
{
    use HasFactory;

    protected $fillable = [
        'client_id',
        'class_id',
        'date',
        'expires_at',
    ];

    protected $casts = [
        'date' => 'date',
        'expires_at' => 'date',
    ];

    public function client()
    {
        return $this->belongsTo(Client::class);
    }

    public function classe()
    {
        return $this->belongsTo(Classe::class, 'class_id');
    }

    // ✅ Nueva relación: una inscripción puede tener muchos pagos
    public function payments()
    {
        return $this->hasMany(Payment::class);
    }

    /**
     * Verifica si la inscripción está activa (no expirada)
     */
    public function isActive(): bool
    {
        if (!$this->expires_at) {
            return false; // Si no tiene fecha de expiración, considerar inactiva
        }
        return $this->expires_at->isFuture() || $this->expires_at->isToday();
    }

    /**
     * Verifica si la inscripción está expirada
     */
    public function isExpired(): bool
    {
        return !$this->isActive();
    }

    /**
     * Scope para obtener solo inscripciones activas
     */
    public function scopeActive($query)
    {
        return $query->where('expires_at', '>=', now()->toDateString());
    }

    /**
     * Scope para obtener solo inscripciones expiradas
     */
    public function scopeExpired($query)
    {
        return $query->where('expires_at', '<', now()->toDateString());
    }
}
