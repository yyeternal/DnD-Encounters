from app import db
from app.main import main_blueprint as bp_main
from flask import render_template, flash, redirect, url_for, jsonify, request
from flask_login import login_required, current_user
import sqlalchemy as sqla
from app.main.models import MonsterGroup, PlayerGroup, Combat
from app.main.forms import CreateMonsterForm, CreateMonsterGroupsForm, CreatePlayerGroupsForm, CreatePlayerForm, CreateCombatForm, FieldList, FormField, BooleanField, DeleteCombatForm
import uuid
import os
from sqlalchemy.orm import joinedload


@bp_main.route('/', methods=['GET'])
@bp_main.route('/index', methods=['GET'])
@login_required
def index():
    return render_template('index.html', title='DnD Encounter Difficulty Calculator')

@bp_main.route('/monster-groups', methods=['GET', 'POST'])
@login_required
def create_monster_groups():
    form = CreateMonsterGroupsForm()
    if form.validate_on_submit():
        print("Form submitted successfully!")
        try:
            new_groups = []

            for group_form in form.monster_groups.data:
                challenge_rating = float(group_form['challenge_rating'])
                quantity = int(group_form['quantity'])

                group_id = f"MG{uuid.uuid4().hex[:6].upper()}"

                new_group = MonsterGroup(
                    challenge_rating=challenge_rating,
                    quantity=quantity,
                    user_id=current_user.id
                )
                new_group.id = group_id  # Set custom group ID after instantiation
                new_group.set_power()  # Set the power using the CR_POWER_MAPPING
                new_groups.append(new_group)

            try:
                db.session.add_all(new_groups)  # Add all groups at once
                db.session.commit()
            except Exception as e:
                import traceback
                traceback.print_exc()  
                print(f"Error creating monster groups: {e}")

            flash("Monster groups created successfully!", "success")
            return redirect(url_for('main.create_player_groups'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error creating monster groups: {str(e)}", "error")
            return redirect(url_for('main.index'))

    return render_template('create_monster.html', form=form)

@bp_main.route('/player-groups', methods=['GET', 'POST'])
@login_required
def create_player_groups():
    form = CreatePlayerGroupsForm()
    if form.validate_on_submit():
        print("Form submitted successfully!")
        try:
            new_groups = []

            for group_form in form.player_groups.data:
                level = float(group_form['level'])
                quantity = int(group_form['quantity'])

                group_id = f"PG{uuid.uuid4().hex[:6].upper()}"

                new_group = PlayerGroup(
                    level=level,
                    quantity=quantity, 
                    user_id = current_user.id
                )
                new_group.id = group_id  
                new_group.set_power()  
                new_groups.append(new_group)

            try:
                db.session.add_all(new_groups)  
                db.session.commit()
            except Exception as e:
                import traceback
                traceback.print_exc()  
                print(f"Error creating player groups: {e}")

            flash("Player groups created successfully!", "success")
            return redirect(url_for('main.create_combat'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error creating player groups: {str(e)}", "error")
            return redirect(url_for('main.index'))

    return render_template('create_player.html', form=form)

@bp_main.route('/create-combat', methods=['GET', 'POST'])
@login_required
def create_combat():
    form = CreateCombatForm()
    
    # Populate choices for player and monster groups
    form.player.choices = [(pg.id, f"Level {pg.level} - {pg.quantity} Players") for pg in PlayerGroup.query.filter_by(user_id=current_user.id).all()]
    form.monster.choices = [(mg.id, f"CR {mg.challenge_rating} - {mg.quantity} Monsters") for mg in MonsterGroup.query.filter_by(user_id=current_user.id).all()]
    
    if form.validate_on_submit():
        selected_player_ids = form.player.data  
        selected_monster_ids = form.monster.data 
        
        # Fetch the PlayerGroup and MonsterGroup instances from the database
        selected_players = PlayerGroup.query.filter(PlayerGroup.id.in_(selected_player_ids)).all()
        selected_monsters = MonsterGroup.query.filter(MonsterGroup.id.in_(selected_monster_ids)).all()
        
        # Check if all player and monster groups exist
        if len(selected_players) != len(selected_player_ids) or len(selected_monsters) != len(selected_monster_ids):
            flash("One or more of the selected groups don't exist.", 'danger')
            return redirect(url_for('main.create_combat'))

        # Create a new Combat instance
        combat = Combat(id=f"CB{uuid.uuid4().hex[:6].upper()}", 
            multiplier=0.0,  
            cost=0, 
            user_id = current_user.id )
        
        combat.player_groups.extend(selected_players)  
        combat.monster_groups.extend(selected_monsters)
        
        combat.calc_multiplier()
        combat.set_cost()
        
        # Commit to the database
        db.session.add(combat)
        db.session.commit()
        
        flash("Combat successfully created!", 'success')
        return redirect(url_for('main.combat_summary'))
    
    return render_template('create_combat.html', form=form)

@bp_main.route('/combat-summary', methods=['GET', 'POST'])
@login_required
def combat_summary():
    combats = Combat.query.filter_by(user_id=current_user.id).all()           
    total_cost = Combat.total_cost(current_user.id)
    form = DeleteCombatForm()      
    if request.method == 'POST':
        combat_id = request.form.get('combat_id')  
        combat = Combat.query.filter_by(id=combat_id, user_id=current_user.id).first()
        if combat:
            try:
                db.session.delete(combat) 
                db.session.commit()
                flash('Combat deleted successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error deleting combat: {e}', 'danger')
        else:
            flash('Combat not found!', 'danger')
        return redirect(url_for('main.combat_summary'))      
    return render_template('combat_summary.html', combats=combats, total_cost=total_cost, form=form)

@bp_main.route('/combat/<combat_id>', methods=['GET'])
@login_required
def view_combat(combat_id):
    combat = Combat.query.options(
        joinedload(Combat.player_groups),
        joinedload(Combat.monster_groups)
    ).filter_by(id=combat_id, user_id=current_user.id).first_or_404()
    return render_template('view_combat.html', combat=combat)

@bp_main.route('/delete-player-group/<string:group_id>', methods=['POST'])
@login_required
def delete_player_group(group_id):
    player_group = PlayerGroup.query.get(group_id)
    if player_group:
        try:
            db.session.delete(player_group)
            db.session.commit()
            flash('Player group deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting player group: {e}', 'danger')
    else:
        flash('Player group not found!', 'danger')
    return redirect(url_for('main.create_player_groups'))

@bp_main.route('/delete-monster-group/<string:group_id>', methods=['POST'])
@login_required
def delete_monster_group(group_id):
    monster_group = MonsterGroup.query.get(group_id)
    if monster_group:
        try:
            db.session.delete(monster_group)
            db.session.commit()
            flash('Monster group deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting monster group: {e}', 'danger')
    else:
        flash('Monster group not found!', 'danger')
    return redirect(url_for('main.create_monster_groups'))