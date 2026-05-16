<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Payment extends Model
{
    use HasFactory;

    protected $fillable = [
        'inscription_id',
        'amount',
        'date',
    ];

    protected $casts = [
        'date' => 'date',
    ];

    // ✅ Un pago pertenece a una inscripción
    public function inscription()
    {
        return $this->belongsTo(Inscription::class);
    }
}
