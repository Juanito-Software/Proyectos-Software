<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Classe extends Model
{
    use HasFactory;

    protected $table = 'classes'; // fuerza el nombre correcto de la tabla

    protected $fillable = [
        'name',
        'desc',
        'coach_id',
        'days',
        'init_hour',
        'final_hour',
    ];

    // Una clase pertenece a un entrenador
    public function coach()
    {
        return $this->belongsTo(Coach::class);
    }

    // Una clase tiene muchas inscripciones
    public function inscriptions()
    {
        return $this->hasMany(Inscription::class, 'class_id');
    }

    // Clientes inscritos en esta clase (a través de inscriptions)
    public function clients()
    {
        return $this->belongsToMany(Client::class, 'inscriptions', 'class_id', 'client_id');
    }
}
