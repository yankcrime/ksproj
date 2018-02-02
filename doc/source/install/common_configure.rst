2. Edit the ``/etc/ksproj/ksproj.conf`` file and complete the following
   actions:

   * In the ``[database]`` section, configure database access:

     .. code-block:: ini

        [database]
        ...
        connection = mysql+pymysql://ksproj:KSPROJ_DBPASS@controller/ksproj
