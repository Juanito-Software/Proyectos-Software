<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Client extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id',
        'name',
        'email',
        'phone_number',
    ];

    // Relación con User
    public function user()
    {
        return $this->belongsTo(User::class);
    }

    // Un cliente puede tener muchas inscripciones
    public function inscriptions()
    {
        return $this->hasMany(Inscription::class);
    }

    // Un cliente puede tener muchos pagos a través de sus inscripciones
    public function payments()
    {
        return $this->hasManyThrough(Payment::class, Inscription::class);
    }

    // Clases a las que está inscrito (a través de inscriptions)
    public function classes()
    {
        return $this->belongsToMany(Inscription::class, 'inscriptions');
    }
}
